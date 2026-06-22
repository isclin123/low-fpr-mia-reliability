from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "05_analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.attacks import EPS, true_class_probabilities
from mia_eval.data import DEFAULT_RANDOM_STATE, default_project_root
from mia_eval.metrics import attack_auc, operating_point_at_fpr
from mia_eval.models import build_model, load_clean_split, predict_proba_for_labels


SCORE_NAMES = ("ref_centered_neg_loss", "ref_logit_margin", "ref_z_logit_margin")
FPR_LEVELS = (0.01, 0.001)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def logit(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(np.asarray(values, dtype=np.float64), EPS, 1.0 - EPS)
    return np.log(clipped / (1.0 - clipped))


def true_probabilities_for_indices(model: Any, X: np.ndarray, y: np.ndarray, labels: np.ndarray) -> np.ndarray:
    probabilities = predict_proba_for_labels(model, X, labels)
    return true_class_probabilities(probabilities, y, labels)


def summarize_scores(
    *,
    member_scores: dict[str, np.ndarray],
    nonmember_scores: dict[str, np.ndarray],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group, scores in (("member", member_scores), ("nonmember", nonmember_scores)):
        for score_name, values in scores.items():
            rows.append(
                {
                    "group": group,
                    "score": score_name,
                    "n": int(len(values)),
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                    "min": float(np.min(values)),
                    "p25": float(np.quantile(values, 0.25)),
                    "median": float(np.quantile(values, 0.5)),
                    "p75": float(np.quantile(values, 0.75)),
                    "max": float(np.max(values)),
                }
            )
    return rows


def metric_rows(
    *,
    dataset: str,
    model: str,
    score_source: str,
    member_scores: dict[str, np.ndarray],
    nonmember_scores: dict[str, np.ndarray],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for score_name in member_scores:
        members = member_scores[score_name]
        nonmembers = nonmember_scores[score_name]
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "score_source": score_source,
                "attack_score": score_name,
                "metric": "AUC",
                "value": float(attack_auc(members, nonmembers)),
                "threshold": "",
                "empirical_fpr": "",
                "tie_fraction": "",
                "n_members": int(len(members)),
                "n_nonmembers": int(len(nonmembers)),
            }
        )
        for fpr in FPR_LEVELS:
            op = operating_point_at_fpr(members, nonmembers, fpr)
            rows.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "score_source": score_source,
                    "attack_score": score_name,
                    "metric": f"TPR@{fpr:g}FPR",
                    "value": float(op["tpr"]),
                    "threshold": float(op["threshold"]),
                    "empirical_fpr": float(op["fpr"]),
                    "tie_fraction": float(op["tie_fraction"]),
                    "n_members": int(len(members)),
                    "n_nonmembers": int(len(nonmembers)),
                }
            )
    return rows


def run_appendix(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    split = load_clean_split(project_root, args.dataset)
    output_dir = (project_root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir
    score_dir = output_dir / "score_arrays"
    score_dir.mkdir(parents=True, exist_ok=True)

    target_model_dir = (
        project_root
        / "05_analysis"
        / "results"
        / args.target_model_subdir
        / args.dataset
        / args.model
    )
    target_model_path = target_model_dir / "model.joblib"
    target_indices_path = target_model_dir / "training_indices.npz"
    target_metadata_path = target_model_dir / "metadata.json"
    if not target_model_path.exists():
        raise FileNotFoundError(f"Missing target model: {target_model_path}")
    if not target_indices_path.exists():
        raise FileNotFoundError(f"Missing target indices: {target_indices_path}")
    if not target_metadata_path.exists():
        raise FileNotFoundError(f"Missing target metadata: {target_metadata_path}")

    target_model = joblib.load(target_model_path)
    target_indices = np.load(target_indices_path)
    member_idx = target_indices["train_idx"].astype(np.int64, copy=False)
    nonmember_idx = target_indices["nonmember_idx"].astype(np.int64, copy=False)
    eval_idx = np.concatenate([member_idx, nonmember_idx])
    labels = np.unique(split.y)

    target_true_probs = true_probabilities_for_indices(
        target_model,
        split.X[eval_idx],
        split.y[eval_idx],
        labels,
    )
    target_neg_loss = np.log(np.clip(target_true_probs, EPS, 1.0))
    target_logit = logit(target_true_probs)

    n_eval = len(eval_idx)
    ref_neg_loss_sum = np.zeros(n_eval, dtype=np.float64)
    ref_logit_sum = np.zeros(n_eval, dtype=np.float64)
    ref_logit_sq_sum = np.zeros(n_eval, dtype=np.float64)
    ref_holdout_count = np.zeros(n_eval, dtype=np.int64)
    ref_all_neg_loss_sum = np.zeros(n_eval, dtype=np.float64)
    ref_all_logit_sum = np.zeros(n_eval, dtype=np.float64)
    ref_all_logit_sq_sum = np.zeros(n_eval, dtype=np.float64)

    eval_position = np.full(len(split.y), -1, dtype=np.int64)
    eval_position[eval_idx] = np.arange(n_eval, dtype=np.int64)
    all_indices = np.arange(len(split.y), dtype=np.int64)
    ref_rows: list[dict[str, Any]] = []

    started = time.perf_counter()
    for ref_id in range(args.n_reference_models):
        seed = args.random_state + 1000 + ref_id
        train_idx, _ = train_test_split(
            all_indices,
            train_size=args.reference_train_fraction,
            random_state=seed,
            stratify=split.y,
        )
        train_idx = np.asarray(train_idx, dtype=np.int64)
        model = build_model(
            args.model,
            random_state=seed,
            n_estimators=args.reference_n_estimators,
            n_jobs=args.n_jobs,
            max_iter=args.max_iter,
        )
        fit_started = time.perf_counter()
        model.fit(split.X[train_idx], split.y[train_idx])
        fit_seconds = time.perf_counter() - fit_started

        ref_true_probs = true_probabilities_for_indices(model, split.X[eval_idx], split.y[eval_idx], labels)
        ref_neg_loss = np.log(np.clip(ref_true_probs, EPS, 1.0))
        ref_logits = logit(ref_true_probs)

        ref_all_neg_loss_sum += ref_neg_loss
        ref_all_logit_sum += ref_logits
        ref_all_logit_sq_sum += ref_logits * ref_logits

        in_train = np.zeros(len(split.y), dtype=bool)
        in_train[train_idx] = True
        holdout_mask = ~in_train[eval_idx]
        ref_neg_loss_sum[holdout_mask] += ref_neg_loss[holdout_mask]
        ref_logit_sum[holdout_mask] += ref_logits[holdout_mask]
        ref_logit_sq_sum[holdout_mask] += ref_logits[holdout_mask] * ref_logits[holdout_mask]
        ref_holdout_count[holdout_mask] += 1

        ref_rows.append(
            {
                "reference_model": ref_id,
                "random_state": seed,
                "train_size": int(len(train_idx)),
                "reference_train_fraction": float(args.reference_train_fraction),
                "fit_seconds": float(fit_seconds),
                "eval_holdout_count": int(np.sum(holdout_mask)),
            }
        )

    used_fallback = ref_holdout_count < args.min_holdout_references
    ref_mean_neg_loss = np.empty(n_eval, dtype=np.float64)
    ref_mean_logit = np.empty(n_eval, dtype=np.float64)
    ref_std_logit = np.empty(n_eval, dtype=np.float64)

    valid = ~used_fallback
    ref_mean_neg_loss[valid] = ref_neg_loss_sum[valid] / ref_holdout_count[valid]
    ref_mean_logit[valid] = ref_logit_sum[valid] / ref_holdout_count[valid]
    ref_logit_var = np.maximum(ref_logit_sq_sum[valid] / ref_holdout_count[valid] - ref_mean_logit[valid] ** 2, 0.0)
    ref_std_logit[valid] = np.sqrt(ref_logit_var)

    # If a sample is held out by too few reference models, use the full reference
    # ensemble mean and record the fallback count. This keeps the appendix bounded
    # while avoiding undefined sample-level scores.
    ref_mean_neg_loss[used_fallback] = ref_all_neg_loss_sum[used_fallback] / args.n_reference_models
    ref_mean_logit[used_fallback] = ref_all_logit_sum[used_fallback] / args.n_reference_models
    fallback_var = np.maximum(
        ref_all_logit_sq_sum[used_fallback] / args.n_reference_models - ref_mean_logit[used_fallback] ** 2,
        0.0,
    )
    ref_std_logit[used_fallback] = np.sqrt(fallback_var)

    all_scores = {
        "ref_centered_neg_loss": target_neg_loss - ref_mean_neg_loss,
        "ref_logit_margin": target_logit - ref_mean_logit,
        "ref_z_logit_margin": (target_logit - ref_mean_logit) / np.maximum(ref_std_logit, args.min_reference_std),
    }
    split_point = len(member_idx)
    member_scores = {name: values[:split_point].astype(np.float32, copy=False) for name, values in all_scores.items()}
    nonmember_scores = {name: values[split_point:].astype(np.float32, copy=False) for name, values in all_scores.items()}

    score_path = score_dir / "stronger_scores.npz"
    payload: dict[str, np.ndarray] = {
        "member_idx": member_idx,
        "nonmember_idx": nonmember_idx,
        "member_reference_holdout_count": ref_holdout_count[:split_point],
        "nonmember_reference_holdout_count": ref_holdout_count[split_point:],
        "member_reference_fallback": used_fallback[:split_point],
        "nonmember_reference_fallback": used_fallback[split_point:],
    }
    for name in SCORE_NAMES:
        payload[f"member_{name}"] = member_scores[name]
        payload[f"nonmember_{name}"] = nonmember_scores[name]
    np.savez_compressed(score_path, **payload)

    summary_path = score_dir / "score_summary.csv"
    write_csv(summary_path, summarize_scores(member_scores=member_scores, nonmember_scores=nonmember_scores))

    reference_diagnostics_path = score_dir / "reference_model_diagnostics.csv"
    write_csv(reference_diagnostics_path, ref_rows)

    comparison_rows = metric_rows(
        dataset=args.dataset,
        model=args.model,
        score_source="reference_centered",
        member_scores=member_scores,
        nonmember_scores=nonmember_scores,
    )

    baseline_path = (
        project_root
        / "05_analysis"
        / "results"
        / args.baseline_score_subdir
        / args.dataset
        / args.model
        / "attack_scores.npz"
    )
    if baseline_path.exists():
        baseline = np.load(baseline_path)
        comparison_rows.extend(
            metric_rows(
                dataset=args.dataset,
                model=args.model,
                score_source="simple_score_baseline",
                member_scores={"neg_loss": baseline["member_neg_loss"]},
                nonmember_scores={"neg_loss": baseline["nonmember_neg_loss"]},
            )
        )

    comparison_path = output_dir / "comparison_metrics.csv"
    write_csv(comparison_path, comparison_rows)

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    metadata = {
        "generated_at": generated_at,
        "dataset": args.dataset,
        "model": args.model,
        "purpose": "Q1 stronger-score compatibility appendix; not a LiRA/RMIA benchmark.",
        "score_names": list(SCORE_NAMES),
        "score_definitions": {
            "ref_centered_neg_loss": "target log(true-class probability) minus out-of-reference mean log(true-class probability).",
            "ref_logit_margin": "target true-class logit minus out-of-reference mean true-class logit.",
            "ref_z_logit_margin": "ref_logit_margin divided by the out-of-reference true-class logit standard deviation.",
        },
        "target_model_path": str(target_model_path.relative_to(project_root)),
        "target_indices_path": str(target_indices_path.relative_to(project_root)),
        "baseline_score_path": str(baseline_path.relative_to(project_root)) if baseline_path.exists() else "",
        "score_path": str(score_path.relative_to(project_root)),
        "score_summary_path": str(summary_path.relative_to(project_root)),
        "reference_diagnostics_path": str(reference_diagnostics_path.relative_to(project_root)),
        "comparison_metrics_path": str(comparison_path.relative_to(project_root)),
        "member_count": int(len(member_idx)),
        "nonmember_count": int(len(nonmember_idx)),
        "n_reference_models": int(args.n_reference_models),
        "reference_n_estimators": int(args.reference_n_estimators),
        "reference_train_fraction": float(args.reference_train_fraction),
        "min_holdout_references": int(args.min_holdout_references),
        "fallback_count": int(np.sum(used_fallback)),
        "member_fallback_count": int(np.sum(used_fallback[:split_point])),
        "nonmember_fallback_count": int(np.sum(used_fallback[split_point:])),
        "min_reference_holdout_count": int(np.min(ref_holdout_count)),
        "median_reference_holdout_count": float(np.median(ref_holdout_count)),
        "max_reference_holdout_count": int(np.max(ref_holdout_count)),
        "random_state": int(args.random_state),
        "fit_seconds_total": float(time.perf_counter() - started),
    }
    metadata_path = score_dir / "metadata.json"
    write_json(metadata_path, metadata)
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a bounded Q1 stronger-score appendix demonstration.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--dataset", default="credit_default")
    parser.add_argument("--model", default="random_forest")
    parser.add_argument("--target-model-subdir", default="expanded_tabular_stage1/models")
    parser.add_argument("--baseline-score-subdir", default="expanded_tabular_stage1/attack_scores")
    parser.add_argument("--output-dir", type=Path, default=Path("05_analysis/results/q1_stronger_score_appendix/credit_default_random_forest"))
    parser.add_argument("--n-reference-models", type=int, default=12)
    parser.add_argument("--reference-n-estimators", type=int, default=100)
    parser.add_argument("--reference-train-fraction", type=float, default=0.5)
    parser.add_argument("--min-holdout-references", type=int, default=3)
    parser.add_argument("--min-reference-std", type=float, default=1e-6)
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--max-iter", type=int, default=1000)
    return parser.parse_args()


def main() -> None:
    metadata = run_appendix(parse_args())
    print(f"wrote {metadata['score_path']}")
    print(f"comparison_metrics={metadata['comparison_metrics_path']}")
    print(f"fallback_count={metadata['fallback_count']}")
    print(f"fit_seconds_total={metadata['fit_seconds_total']:.2f}")


if __name__ == "__main__":
    main()
