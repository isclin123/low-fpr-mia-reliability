from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.attacks import predict_scores_batched
from mia_eval.audit_tool import AuditToolConfig, run_audit
from mia_eval.data import DEFAULT_RANDOM_STATE, default_project_root
from mia_eval.experiments import FPR_LEVELS, metric_label_for_fpr
from mia_eval.metrics import attack_auc, operating_point_at_fpr
from mia_eval.models import build_model, load_clean_split


SCORE_NAME = "shadow_lira_like_neg_loss"
BASE_SCORE_NAME = "neg_loss"
DEFAULT_DATASETS = ("credit_default", "adult_income")
DEFAULT_SAMPLE_SIZES = (500, 1000, 2500, 5000, 10000, 15000, 20000)
DEFAULT_SHADOW_TRAIN_SIZES = {
    "credit_default": 5000,
    "adult_income": 8000,
}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows and fieldnames is None:
        raise ValueError(f"No rows to write for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_output_dir(project_root: Path, output_dir: Path) -> Path:
    return output_dir if output_dir.is_absolute() else project_root / output_dir


def score_path(project_root: Path, attack_score_subdir: str, dataset: str, model: str) -> Path:
    return project_root / "analysis" / "results" / attack_score_subdir / dataset / model / "attack_scores.npz"


def metadata_path(project_root: Path, attack_score_subdir: str, dataset: str, model: str) -> Path:
    return project_root / "analysis" / "results" / attack_score_subdir / dataset / model / "metadata.json"


def load_target_scores(
    project_root: Path,
    *,
    attack_score_subdir: str,
    dataset: str,
    model: str,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    path = score_path(project_root, attack_score_subdir, dataset, model)
    meta_path = metadata_path(project_root, attack_score_subdir, dataset, model)
    if not path.exists():
        raise FileNotFoundError(f"Missing target score array: {path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing target score metadata: {meta_path}")
    loaded = np.load(path)
    arrays = {key: loaded[key] for key in loaded.files}
    return arrays, read_json(meta_path)


def gaussian_logpdf(values: np.ndarray, mean: float, variance: float) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    return -0.5 * (np.log(2.0 * np.pi * variance) + ((values - mean) ** 2) / variance)


def fit_gaussian(values: np.ndarray, *, min_std: float) -> dict[str, float]:
    values = np.asarray(values, dtype=np.float64)
    variance = float(np.var(values, ddof=1)) if len(values) > 1 else 0.0
    variance = max(variance, float(min_std) ** 2)
    return {
        "mean": float(np.mean(values)),
        "std": float(np.sqrt(variance)),
        "variance": variance,
        "n": int(len(values)),
    }


def lira_like_scores(
    target_scores: np.ndarray,
    *,
    shadow_member_fit: dict[str, float],
    shadow_nonmember_fit: dict[str, float],
) -> np.ndarray:
    member_logpdf = gaussian_logpdf(
        target_scores,
        shadow_member_fit["mean"],
        shadow_member_fit["variance"],
    )
    nonmember_logpdf = gaussian_logpdf(
        target_scores,
        shadow_nonmember_fit["mean"],
        shadow_nonmember_fit["variance"],
    )
    return (member_logpdf - nonmember_logpdf).astype(np.float32, copy=False)


def draw_shadow_split(
    y: np.ndarray,
    *,
    train_size: int,
    holdout_size: int,
    random_state: int,
) -> tuple[np.ndarray, np.ndarray]:
    n_rows = len(y)
    if train_size + holdout_size > n_rows:
        max_each = n_rows // 2
        train_size = min(train_size, max_each)
        holdout_size = min(holdout_size, n_rows - train_size)
    indices = np.arange(n_rows, dtype=np.int64)
    train_idx, holdout_idx = train_test_split(
        indices,
        train_size=train_size,
        test_size=holdout_size,
        random_state=random_state,
        stratify=y,
    )
    return train_idx.astype(np.int64), holdout_idx.astype(np.int64)


def train_shadow_score_distributions(
    project_root: Path,
    *,
    dataset: str,
    model: str,
    n_shadows: int,
    shadow_train_size: int,
    shadow_holdout_size: int,
    n_estimators: int,
    n_jobs: int,
    max_iter: int,
    batch_size: int,
    random_state: int,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    split = load_clean_split(project_root, dataset)
    labels = np.unique(split.y)
    shadow_member_parts: list[np.ndarray] = []
    shadow_nonmember_parts: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []

    for shadow_id in range(n_shadows):
        seed = random_state + 1009 * (shadow_id + 1)
        train_idx, holdout_idx = draw_shadow_split(
            split.y,
            train_size=shadow_train_size,
            holdout_size=shadow_holdout_size,
            random_state=seed,
        )
        shadow_model = build_model(
            model,
            random_state=seed,
            n_estimators=n_estimators,
            n_jobs=n_jobs,
            max_iter=max_iter,
        )
        started = time.perf_counter()
        shadow_model.fit(split.X[train_idx], split.y[train_idx])
        fit_seconds = time.perf_counter() - started

        member_scores = predict_scores_batched(
            shadow_model,
            split.X[train_idx],
            split.y[train_idx],
            labels,
            batch_size=batch_size,
        )[BASE_SCORE_NAME]
        nonmember_scores = predict_scores_batched(
            shadow_model,
            split.X[holdout_idx],
            split.y[holdout_idx],
            labels,
            batch_size=batch_size,
        )[BASE_SCORE_NAME]
        shadow_member_parts.append(np.asarray(member_scores, dtype=np.float64))
        shadow_nonmember_parts.append(np.asarray(nonmember_scores, dtype=np.float64))
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "shadow_id": shadow_id,
                "random_state": seed,
                "shadow_train_size": int(len(train_idx)),
                "shadow_holdout_size": int(len(holdout_idx)),
                "fit_seconds": float(fit_seconds),
                "shadow_member_neg_loss_mean": float(np.mean(member_scores)),
                "shadow_nonmember_neg_loss_mean": float(np.mean(nonmember_scores)),
            }
        )

    return np.concatenate(shadow_member_parts), np.concatenate(shadow_nonmember_parts), rows


def point_metric_dict(
    *,
    dataset: str,
    model: str,
    score_source: str,
    score_name: str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "dataset": dataset,
        "model": model,
        "score_source": score_source,
        "attack_score": score_name,
        "n_members": int(len(member_scores)),
        "n_nonmembers": int(len(nonmember_scores)),
        "AUC": float(attack_auc(member_scores, nonmember_scores)),
    }
    for fpr in FPR_LEVELS:
        op = operating_point_at_fpr(member_scores, nonmember_scores, fpr)
        row[metric_label_for_fpr("TPR", fpr)] = float(op["tpr"])
        row[f"{metric_label_for_fpr('TPR', fpr)}_threshold"] = float(op["threshold"])
        row[f"{metric_label_for_fpr('TPR', fpr)}_empirical_fpr"] = float(op["fpr"])
        row[f"{metric_label_for_fpr('TPR', fpr)}_tie_fraction"] = float(op["tie_fraction"])
    return row


def write_score_csv(
    path: Path,
    *,
    dataset: str,
    model: str,
    member_idx: np.ndarray,
    nonmember_idx: np.ndarray,
    member_base: np.ndarray,
    nonmember_base: np.ndarray,
    member_lira_like: np.ndarray,
    nonmember_lira_like: np.ndarray,
) -> None:
    rows: list[dict[str, Any]] = []
    for sample_id, base_score, score in zip(member_idx, member_base, member_lira_like, strict=True):
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "sample_id": int(sample_id),
                "membership": 1,
                BASE_SCORE_NAME: float(base_score),
                SCORE_NAME: float(score),
            }
        )
    for sample_id, base_score, score in zip(nonmember_idx, nonmember_base, nonmember_lira_like, strict=True):
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "sample_id": int(sample_id),
                "membership": 0,
                BASE_SCORE_NAME: float(base_score),
                SCORE_NAME: float(score),
            }
        )
    write_csv(
        path,
        rows,
        fieldnames=["dataset", "model", "sample_id", "membership", BASE_SCORE_NAME, SCORE_NAME],
    )


def run_dataset(args: argparse.Namespace, dataset: str, output_dir: Path) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    model = args.model
    dataset_slug = f"{dataset}_{model}_{SCORE_NAME}"
    arrays_dir = output_dir / "score_arrays"
    tables_dir = output_dir / "tables"
    audit_root = output_dir / "audit_tool" / dataset_slug
    arrays_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    target_arrays, target_metadata = load_target_scores(
        project_root,
        attack_score_subdir=args.attack_score_subdir,
        dataset=dataset,
        model=model,
    )
    member_base = np.asarray(target_arrays[f"member_{BASE_SCORE_NAME}"], dtype=np.float64)
    nonmember_base = np.asarray(target_arrays[f"nonmember_{BASE_SCORE_NAME}"], dtype=np.float64)

    shadow_train_size = args.shadow_train_size or DEFAULT_SHADOW_TRAIN_SIZES.get(dataset, 5000)
    shadow_holdout_size = args.shadow_holdout_size or shadow_train_size
    shadow_member, shadow_nonmember, shadow_rows = train_shadow_score_distributions(
        project_root,
        dataset=dataset,
        model=model,
        n_shadows=args.n_shadows,
        shadow_train_size=shadow_train_size,
        shadow_holdout_size=shadow_holdout_size,
        n_estimators=args.n_estimators,
        n_jobs=args.n_jobs,
        max_iter=args.max_iter,
        batch_size=args.batch_size,
        random_state=args.random_state + 50000 * len(dataset),
    )

    pooled_std = float(np.std(np.concatenate([shadow_member, shadow_nonmember]), ddof=1))
    min_std = max(args.min_shadow_std, pooled_std * args.min_shadow_std_fraction)
    member_fit = fit_gaussian(shadow_member, min_std=min_std)
    nonmember_fit = fit_gaussian(shadow_nonmember, min_std=min_std)
    member_lira_like = lira_like_scores(
        member_base,
        shadow_member_fit=member_fit,
        shadow_nonmember_fit=nonmember_fit,
    )
    nonmember_lira_like = lira_like_scores(
        nonmember_base,
        shadow_member_fit=member_fit,
        shadow_nonmember_fit=nonmember_fit,
    )

    npz_path = arrays_dir / f"{dataset_slug}.npz"
    csv_path = arrays_dir / f"{dataset_slug}.csv"
    np.savez_compressed(
        npz_path,
        member_idx=np.asarray(target_arrays["member_idx"], dtype=np.int64),
        nonmember_idx=np.asarray(target_arrays["nonmember_idx"], dtype=np.int64),
        member_neg_loss=member_base.astype(np.float32, copy=False),
        nonmember_neg_loss=nonmember_base.astype(np.float32, copy=False),
        member_shadow_lira_like_neg_loss=member_lira_like.astype(np.float32, copy=False),
        nonmember_shadow_lira_like_neg_loss=nonmember_lira_like.astype(np.float32, copy=False),
        shadow_member_neg_loss=shadow_member.astype(np.float32, copy=False),
        shadow_nonmember_neg_loss=shadow_nonmember.astype(np.float32, copy=False),
    )
    write_score_csv(
        csv_path,
        dataset=dataset,
        model=model,
        member_idx=np.asarray(target_arrays["member_idx"], dtype=np.int64),
        nonmember_idx=np.asarray(target_arrays["nonmember_idx"], dtype=np.int64),
        member_base=member_base,
        nonmember_base=nonmember_base,
        member_lira_like=member_lira_like,
        nonmember_lira_like=nonmember_lira_like,
    )

    audit_payload = run_audit(
        AuditToolConfig(
            input_path=npz_path,
            input_format="npz",
            output_dir=audit_root,
            score_names=(SCORE_NAME,),
            dataset=dataset,
            model=f"{model}_{SCORE_NAME}",
            fpr_levels=FPR_LEVELS,
            n_bootstrap=args.n_bootstrap,
            confidence=args.confidence,
            n_repeats=args.n_repeats,
            sample_sizes=tuple(args.sample_sizes),
            random_state=args.random_state,
            make_figures=not args.skip_figures,
        )
    )

    fit_row = {
        "dataset": dataset,
        "model": model,
        "score_name": SCORE_NAME,
        "n_shadows": int(args.n_shadows),
        "shadow_train_size": int(shadow_train_size),
        "shadow_holdout_size": int(shadow_holdout_size),
        "shadow_member_n": int(len(shadow_member)),
        "shadow_nonmember_n": int(len(shadow_nonmember)),
        "shadow_member_neg_loss_mean": member_fit["mean"],
        "shadow_member_neg_loss_std": member_fit["std"],
        "shadow_nonmember_neg_loss_mean": nonmember_fit["mean"],
        "shadow_nonmember_neg_loss_std": nonmember_fit["std"],
        "min_std_used": float(min_std),
        "npz_path": str(npz_path.relative_to(project_root)),
        "csv_path": str(csv_path.relative_to(project_root)),
        "audit_output_dir": str(audit_root.relative_to(project_root)),
    }
    metrics_rows = [
        point_metric_dict(
            dataset=dataset,
            model=model,
            score_source="target_base_neg_loss",
            score_name=BASE_SCORE_NAME,
            member_scores=member_base,
            nonmember_scores=nonmember_base,
        ),
        point_metric_dict(
            dataset=dataset,
            model=model,
            score_source="bounded_shadow_lira_like",
            score_name=SCORE_NAME,
            member_scores=member_lira_like,
            nonmember_scores=nonmember_lira_like,
        ),
    ]
    return {
        "dataset": dataset,
        "model": model,
        "target_metadata": target_metadata,
        "fit_row": fit_row,
        "shadow_rows": shadow_rows,
        "metrics_rows": metrics_rows,
        "audit_payload": audit_payload,
    }


def summary_markdown(config: dict[str, Any], metrics_rows: list[dict[str, Any]], fit_rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Q1 Bounded LiRA-Like Shadow Score Appendix",
        "",
        f"Generated: {config['generated_at']}",
        "",
        "## Scope",
        "",
        "This is a bounded score-array compatibility case for the reusable audit workflow. It is not a full LiRA benchmark, not an RMIA benchmark, and not a claim that the implemented score is a state-of-the-art membership attack.",
        "",
        "The score is a global shadow-model log-likelihood ratio over target-model `neg_loss`:",
        "",
        "`log p(target neg_loss | shadow train scores) - log p(target neg_loss | shadow holdout scores)`",
        "",
        "The shadow distributions are Gaussian fits pooled across a small number of random-forest shadow models trained with the same cleaned data representation and target-model family.",
        "",
        "## Key Metrics",
        "",
        "| Dataset | Score source | Attack score | AUC | TPR@1%FPR | TPR@0.1%FPR | Members | Non-members |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in metrics_rows:
        lines.append(
            f"| {row['dataset']} | {row['score_source']} | {row['attack_score']} | "
            f"{row['AUC']:.4f} | {row['TPR@1%FPR']:.4f} | {row['TPR@0.1%FPR']:.4f} | "
            f"{row['n_members']} | {row['n_nonmembers']} |"
        )
    lines.extend(
        [
            "",
            "## Shadow Fit Summary",
            "",
            "| Dataset | Shadows | Train/holdout per shadow | Shadow train mean/std | Shadow holdout mean/std |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in fit_rows:
        lines.append(
            f"| {row['dataset']} | {row['n_shadows']} | {row['shadow_train_size']} / {row['shadow_holdout_size']} | "
            f"{row['shadow_member_neg_loss_mean']:.4f} / {row['shadow_member_neg_loss_std']:.4f} | "
            f"{row['shadow_nonmember_neg_loss_mean']:.4f} / {row['shadow_nonmember_neg_loss_std']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Score arrays: `{config['arrays_dir']}`",
            f"- Audit-tool outputs: `{config['audit_dir']}`",
            f"- Summary tables: `{config['tables_dir']}`",
            f"- Run config: `{config['config_path']}`",
            "",
            "## Limitations",
            "",
            "- This uses global shadow train/holdout score distributions, not per-example in/out shadow distributions as in full LiRA.",
            "- The Gaussian density model is a lightweight compatibility device over `neg_loss`; no RMIA offline/online ratio, population prior, or difficulty calibration is implemented.",
            "- Shadow models are bounded in count and training size for appendix evidence, so the result should be interpreted as an audit-tool compatibility case rather than an attack benchmark.",
            "- Target member and non-member score arrays come from the existing target RF artifacts and existing member/non-member split.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_appendix(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    output_dir = resolve_output_dir(project_root, args.output_dir)
    arrays_dir = output_dir / "score_arrays"
    tables_dir = output_dir / "tables"
    audit_dir = output_dir / "audit_tool"
    for path in (arrays_dir, tables_dir, audit_dir):
        path.mkdir(parents=True, exist_ok=True)

    dataset_payloads = [run_dataset(args, dataset, output_dir) for dataset in args.datasets]
    fit_rows = [payload["fit_row"] for payload in dataset_payloads]
    shadow_rows = [row for payload in dataset_payloads for row in payload["shadow_rows"]]
    metrics_rows = [row for payload in dataset_payloads for row in payload["metrics_rows"]]

    fit_path = tables_dir / "shadow_fit_summary.csv"
    shadow_path = tables_dir / "shadow_model_runs.csv"
    metrics_path = tables_dir / "key_metrics.csv"
    config_path = output_dir / "run_config.json"
    summary_path = output_dir / "README.md"

    write_csv(fit_path, fit_rows)
    write_csv(shadow_path, shadow_rows)
    write_csv(metrics_path, metrics_rows)

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    config = {
        "generated_at": generated_at,
        "purpose": "Bounded LiRA-like/shadow-model score-array compatibility case for Q1 appendix.",
        "not_full_lira_or_rmia": True,
        "project_root": str(project_root),
        "datasets": list(args.datasets),
        "model": args.model,
        "base_score": BASE_SCORE_NAME,
        "score_name": SCORE_NAME,
        "attack_score_subdir": args.attack_score_subdir,
        "n_shadows": int(args.n_shadows),
        "n_estimators": int(args.n_estimators),
        "n_jobs": int(args.n_jobs),
        "max_iter": int(args.max_iter),
        "batch_size": int(args.batch_size),
        "n_bootstrap": int(args.n_bootstrap),
        "confidence": float(args.confidence),
        "n_repeats": int(args.n_repeats),
        "sample_sizes": list(args.sample_sizes),
        "random_state": int(args.random_state),
        "skip_figures": bool(args.skip_figures),
        "arrays_dir": str(arrays_dir.relative_to(project_root)),
        "audit_dir": str(audit_dir.relative_to(project_root)),
        "tables_dir": str(tables_dir.relative_to(project_root)),
        "fit_summary_path": str(fit_path.relative_to(project_root)),
        "shadow_model_runs_path": str(shadow_path.relative_to(project_root)),
        "key_metrics_path": str(metrics_path.relative_to(project_root)),
        "config_path": str(config_path.relative_to(project_root)),
        "summary_path": str(summary_path.relative_to(project_root)),
        "dataset_outputs": [
            {
                "dataset": payload["dataset"],
                "model": payload["model"],
                "score_arrays": payload["fit_row"]["npz_path"],
                "score_arrays_csv": payload["fit_row"]["csv_path"],
                "audit_output_dir": payload["fit_row"]["audit_output_dir"],
            }
            for payload in dataset_payloads
        ],
    }
    write_json(config_path, config)
    summary_path.write_text(summary_markdown(config, metrics_rows, fit_rows), encoding="utf-8")
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded LiRA-like shadow score-array appendix case.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--datasets", nargs="+", default=list(DEFAULT_DATASETS), choices=list(DEFAULT_DATASETS))
    parser.add_argument("--model", default="random_forest", choices=["random_forest"])
    parser.add_argument("--attack-score-subdir", default="expanded_tabular_stage1/attack_scores")
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/results/q1_lira_like_appendix"))
    parser.add_argument("--n-shadows", type=int, default=8)
    parser.add_argument("--shadow-train-size", type=int)
    parser.add_argument("--shadow-holdout-size", type=int)
    parser.add_argument("--n-estimators", type=int, default=80)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=50000)
    parser.add_argument("--min-shadow-std", type=float, default=1e-4)
    parser.add_argument("--min-shadow-std-fraction", type=float, default=0.02)
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--n-repeats", type=int, default=200)
    parser.add_argument("--sample-sizes", nargs="+", type=int, default=list(DEFAULT_SAMPLE_SIZES))
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    parser.add_argument("--skip-figures", action="store_true")
    return parser.parse_args()


def main() -> None:
    config = run_appendix(parse_args())
    print(f"summary={config['summary_path']}")
    print(f"key_metrics={config['key_metrics_path']}")
    print(f"score_arrays={config['arrays_dir']}")
    print(f"audit_outputs={config['audit_dir']}")


if __name__ == "__main__":
    main()
