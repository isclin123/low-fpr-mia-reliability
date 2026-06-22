from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.attacks import SCORE_NAMES, predict_scores_batched
from mia_eval.data import DEFAULT_RANDOM_STATE, default_project_root
from mia_eval.experiments import FPR_LEVELS, metric_label_for_fpr
from mia_eval.metrics import attack_auc, operating_point_at_fpr
from mia_eval.models import build_model, evaluate_classifier, load_clean_split


DEFAULT_SETTINGS = (
    ("credit_default", "random_forest", "CD/RF"),
    ("credit_default", "extra_trees", "CD/ET"),
    ("adult_income", "random_forest", "Adult/RF"),
)
DEFAULT_SEEDS = (20260602, 20260603, 20260604, 20260605, 20260606)


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


def parse_setting(value: str) -> tuple[str, str, str]:
    parts = value.split(":")
    if len(parts) == 2:
        dataset, model = parts
        label = f"{dataset}/{model}"
    elif len(parts) == 3:
        dataset, model, label = parts
    else:
        raise argparse.ArgumentTypeError("settings must be dataset:model[:label]")
    return dataset, model, label


def metric_rows_for_scores(
    *,
    dataset: str,
    model: str,
    setting: str,
    split_seed: int,
    model_seed: int,
    score_name: str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    train_eval: dict[str, float],
    nonmember_eval: dict[str, float],
    fit_seconds: float,
) -> list[dict[str, Any]]:
    common = {
        "dataset": dataset,
        "model": model,
        "setting": setting,
        "split_seed": int(split_seed),
        "model_seed": int(model_seed),
        "attack_score": score_name,
        "n_members": int(len(member_scores)),
        "n_nonmembers": int(len(nonmember_scores)),
        "train_accuracy": float(train_eval["accuracy"]),
        "nonmember_accuracy": float(nonmember_eval["accuracy"]),
        "accuracy_gap": float(train_eval["accuracy"] - nonmember_eval["accuracy"]),
        "train_log_loss": float(train_eval["log_loss"]),
        "nonmember_log_loss": float(nonmember_eval["log_loss"]),
        "log_loss_gap": float(nonmember_eval["log_loss"] - train_eval["log_loss"]),
        "fit_seconds": float(fit_seconds),
    }
    rows = [
        {
            **common,
            "metric": "AUC",
            "value": float(attack_auc(member_scores, nonmember_scores)),
            "threshold": "",
            "empirical_fpr": "",
            "tie_fraction": "",
        }
    ]
    for fpr in FPR_LEVELS:
        op = operating_point_at_fpr(member_scores, nonmember_scores, fpr)
        rows.append(
            {
                **common,
                "metric": metric_label_for_fpr("TPR", fpr),
                "value": float(op["tpr"]),
                "threshold": float(op["threshold"]),
                "empirical_fpr": float(op["fpr"]),
                "tie_fraction": float(op["tie_fraction"]),
            }
        )
    return rows


def summarize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        grouped[
            (
                str(row["dataset"]),
                str(row["model"]),
                str(row["attack_score"]),
                str(row["metric"]),
            )
        ].append(float(row["value"]))

    summary_rows: list[dict[str, Any]] = []
    for (dataset, model, score_name, metric), values in sorted(grouped.items()):
        arr = np.asarray(values, dtype=float)
        summary_rows.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "metric": metric,
                "n_repeats": int(len(arr)),
                "mean": float(np.mean(arr)),
                "sd": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "range": float(np.max(arr) - np.min(arr)),
            }
        )
    return summary_rows


def paper_rows_from_summary(
    metric_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_setting = {
        (dataset, model): label
        for dataset, model, label in DEFAULT_SETTINGS
    }
    summary_lookup = {
        (
            str(row["dataset"]),
            str(row["model"]),
            str(row["attack_score"]),
            str(row["metric"]),
        ): row
        for row in summary_rows
    }
    gap_grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in metric_rows:
        if row["attack_score"] == "neg_loss" and row["metric"] == "AUC":
            gap_grouped[(str(row["dataset"]), str(row["model"]))].append(float(row["accuracy_gap"]))

    paper_rows: list[dict[str, Any]] = []
    for dataset, model, setting in DEFAULT_SETTINGS:
        auc = summary_lookup[(dataset, model, "neg_loss", "AUC")]
        tpr1 = summary_lookup[(dataset, model, "neg_loss", "TPR@1%FPR")]
        tpr01 = summary_lookup[(dataset, model, "neg_loss", "TPR@0.1%FPR")]
        gaps = np.asarray(gap_grouped[(dataset, model)], dtype=float)
        paper_rows.append(
            {
                "setting": by_setting.get((dataset, model), setting),
                "dataset": dataset,
                "model": model,
                "n_repeats": int(auc["n_repeats"]),
                "auc_mean": auc["mean"],
                "auc_min": auc["min"],
                "auc_max": auc["max"],
                "tpr1_mean": tpr1["mean"],
                "tpr1_min": tpr1["min"],
                "tpr1_max": tpr1["max"],
                "tpr001_mean": tpr01["mean"],
                "tpr001_min": tpr01["min"],
                "tpr001_max": tpr01["max"],
                "accuracy_gap_mean": float(np.mean(gaps)),
                "accuracy_gap_min": float(np.min(gaps)),
                "accuracy_gap_max": float(np.max(gaps)),
            }
        )
    return paper_rows


def fmt_mean_range(row: dict[str, Any], prefix: str) -> str:
    return f"{float(row[prefix + '_mean']):.4f} [{float(row[prefix + '_min']):.4f}, {float(row[prefix + '_max']):.4f}]"


def write_summary(
    path: Path,
    *,
    config: dict[str, Any],
    paper_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Q1 Split/Seed Sensitivity",
        "",
        "This bounded check repeats the target member/non-member split and target-model random seed, then recomputes negative-loss member/non-member score arrays and low-FPR metrics.",
        "",
        "It is a combined split-plus-seed sensitivity check. It is not a factorial decomposition of split variability versus learner-seed variability, and it is not a new attack benchmark.",
        "",
        "## Paper-ready table",
        "",
        "| Setting | Repeats | AUC mean [min, max] | TPR@1%FPR mean [min, max] | TPR@0.1%FPR mean [min, max] | Accuracy gap mean [min, max] |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in paper_rows:
        lines.append(
            "| {setting} | {repeats} | {auc} | {tpr1} | {tpr001} | {gap} |".format(
                setting=row["setting"],
                repeats=row["n_repeats"],
                auc=fmt_mean_range(row, "auc"),
                tpr1=fmt_mean_range(row, "tpr1"),
                tpr001=fmt_mean_range(row, "tpr001"),
                gap=fmt_mean_range(row, "accuracy_gap"),
            )
        )
    lines.extend(
        [
            "",
            "## Design",
            "",
            f"- Split/model seeds: `{config['seeds']}`",
            f"- Settings: `{config['settings']}`",
            f"- Scores evaluated: `{config['score_names']}`",
            f"- Random forest / ExtraTrees estimators: `{config['n_estimators']}`",
            f"- Maximum iterations for iterative estimators: `{config['max_iter']}`",
            "",
            "## Outputs",
            "",
            f"- Per-seed metric rows: `{config['metric_rows_path']}`",
            f"- Metric summaries: `{config['summary_rows_path']}`",
            f"- Paper table: `{config['paper_table_path']}`",
            f"- Run config: `{config['run_config_path']}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_sensitivity(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    settings = list(args.settings)
    seeds = [int(seed) for seed in args.seeds]
    score_names = tuple(args.score_names)

    metric_rows: list[dict[str, Any]] = []
    for dataset, model_name, setting_label in settings:
        split = load_clean_split(project_root, dataset)
        labels = np.unique(split.y)
        all_indices = np.arange(len(split.y), dtype=np.int64)

        for seed in seeds:
            member_idx, nonmember_idx = train_test_split(
                all_indices,
                test_size=0.5,
                random_state=seed,
                stratify=split.y,
            )
            member_idx = np.asarray(member_idx, dtype=np.int64)
            nonmember_idx = np.asarray(nonmember_idx, dtype=np.int64)

            target_model = build_model(
                model_name,
                random_state=seed,
                n_estimators=args.n_estimators,
                n_jobs=args.n_jobs,
                max_iter=args.max_iter,
            )
            started = time.perf_counter()
            target_model.fit(split.X[member_idx], split.y[member_idx])
            fit_seconds = time.perf_counter() - started

            train_eval = evaluate_classifier(target_model, split.X[member_idx], split.y[member_idx], labels=labels)
            nonmember_eval = evaluate_classifier(
                target_model,
                split.X[nonmember_idx],
                split.y[nonmember_idx],
                labels=labels,
            )
            member_scores = predict_scores_batched(
                target_model,
                split.X[member_idx],
                split.y[member_idx],
                labels,
                batch_size=args.batch_size,
            )
            nonmember_scores = predict_scores_batched(
                target_model,
                split.X[nonmember_idx],
                split.y[nonmember_idx],
                labels,
                batch_size=args.batch_size,
            )
            for score_name in score_names:
                metric_rows.extend(
                    metric_rows_for_scores(
                        dataset=dataset,
                        model=model_name,
                        setting=setting_label,
                        split_seed=seed,
                        model_seed=seed,
                        score_name=score_name,
                        member_scores=np.asarray(member_scores[score_name], dtype=float),
                        nonmember_scores=np.asarray(nonmember_scores[score_name], dtype=float),
                        train_eval=train_eval,
                        nonmember_eval=nonmember_eval,
                        fit_seconds=fit_seconds,
                    )
                )

    summary_rows = summarize_rows(metric_rows)
    paper_rows = paper_rows_from_summary(metric_rows, summary_rows)

    metric_path = output_dir / "split_seed_metric_rows.csv"
    summary_path = output_dir / "split_seed_summary.csv"
    paper_path = output_dir / "paper_table_split_seed_sensitivity.csv"
    config_path = output_dir / "run_config.json"
    readme_path = output_dir / "q1_split_seed_sensitivity_summary.md"

    write_csv(metric_path, metric_rows)
    write_csv(summary_path, summary_rows)
    write_csv(paper_path, paper_rows)

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    config = {
        "generated_at": generated_at,
        "project_root": str(project_root),
        "settings": [{"dataset": d, "model": m, "label": label} for d, m, label in settings],
        "seeds": seeds,
        "score_names": list(score_names),
        "n_estimators": int(args.n_estimators),
        "n_jobs": int(args.n_jobs),
        "max_iter": int(args.max_iter),
        "batch_size": int(args.batch_size),
        "metric_rows_path": str(metric_path.relative_to(project_root)),
        "summary_rows_path": str(summary_path.relative_to(project_root)),
        "paper_table_path": str(paper_path.relative_to(project_root)),
        "run_config_path": str(config_path.relative_to(project_root)),
        "summary_path": str(readme_path.relative_to(project_root)),
        "design_note": (
            "Each repeat redraws a stratified 50/50 member/non-member split and "
            "uses the same integer as the target-model random seed."
        ),
    }
    write_json(config_path, config)
    write_summary(readme_path, config=config, paper_rows=paper_rows)
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bounded Q1 split/seed sensitivity checks.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/results/q1_split_seed_sensitivity"))
    parser.add_argument("--settings", nargs="+", type=parse_setting, default=list(DEFAULT_SETTINGS))
    parser.add_argument("--seeds", nargs="+", type=int, default=list(DEFAULT_SEEDS))
    parser.add_argument("--score-names", nargs="+", default=["neg_loss"], choices=list(SCORE_NAMES))
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=50000)
    return parser.parse_args()


def main() -> None:
    config = run_sensitivity(parse_args())
    print(f"metrics={config['metric_rows_path']}")
    print(f"summary={config['summary_path']}")


if __name__ == "__main__":
    main()
