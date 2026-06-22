from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any

import numpy as np

from mia_eval.attacks import SCORE_NAMES
from mia_eval.data import DEFAULT_RANDOM_STATE, default_project_root
from mia_eval.experiments import FPR_LEVELS, load_score_arrays, metric_label_for_fpr
from mia_eval.metrics import attack_auc, membership_advantage_at_fpr, tpr_at_fpr
from mia_eval.models import ALL_DATASETS, ALL_MODELS, CORE_DATASETS, CORE_MODELS


DEFAULT_SAMPLE_SIZES = (250, 500, 1000, 2000, 5000)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sample_metric_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    sample_size: int,
    repeat: int,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "dataset": dataset,
            "model": model,
            "attack_score": score_name,
            "sample_size": sample_size,
            "repeat": repeat,
            "metric": "AUC",
            "value": float(attack_auc(member_scores, nonmember_scores)),
            "fp_budget": "",
        }
    ]

    for fpr in FPR_LEVELS:
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "sample_size": sample_size,
                "repeat": repeat,
                "metric": metric_label_for_fpr("TPR", fpr),
                "value": float(tpr_at_fpr(member_scores, nonmember_scores, fpr)),
                "fp_budget": sample_size * fpr,
            }
        )
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "sample_size": sample_size,
                "repeat": repeat,
                "metric": metric_label_for_fpr("membership_advantage", fpr),
                "value": float(membership_advantage_at_fpr(member_scores, nonmember_scores, fpr)),
                "fp_budget": sample_size * fpr,
            }
        )
    return rows


def instability_note(metric: str, sample_size: int) -> str:
    if metric == "TPR@0.1%FPR" or metric == "membership_advantage@0.1%FPR":
        budget = sample_size * 0.001
        if budget < 1:
            return "severe_tail_resolution_warning: expected false positives < 1"
        if budget < 5:
            return "tail_resolution_warning: expected false positives < 5"
    if metric == "TPR@1%FPR" or metric == "membership_advantage@1%FPR":
        budget = sample_size * 0.01
        if budget < 5:
            return "tail_resolution_warning: expected false positives < 5"
    return ""


def aggregate_rows(repeat_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, int, str], list[float]] = {}
    for row in repeat_rows:
        key = (
            str(row["dataset"]),
            str(row["model"]),
            str(row["attack_score"]),
            int(row["sample_size"]),
            str(row["metric"]),
        )
        groups.setdefault(key, []).append(float(row["value"]))

    aggregate: list[dict[str, Any]] = []
    for (dataset, model, score_name, sample_size, metric), values_list in sorted(groups.items()):
        values = np.asarray(values_list, dtype=float)
        lower = float(np.quantile(values, 0.025))
        upper = float(np.quantile(values, 0.975))
        aggregate.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "sample_size": sample_size,
                "metric": metric,
                "n_repeats": int(len(values)),
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                "p025": lower,
                "median": float(np.quantile(values, 0.5)),
                "p975": upper,
                "interval_width": upper - lower,
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "instability_note": instability_note(metric, sample_size),
            }
        )
    return aggregate


def run_subsampling(
    project_root: Path,
    *,
    datasets: list[str],
    models: list[str],
    attack_score_subdir: str,
    output_dir: Path,
    sample_sizes: tuple[int, ...] = DEFAULT_SAMPLE_SIZES,
    n_repeats: int = 200,
    random_state: int = DEFAULT_RANDOM_STATE,
    score_names: tuple[str, ...] = SCORE_NAMES,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(random_state)
    repeat_rows: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for dataset in datasets:
        for model in models:
            arrays, _metadata = load_score_arrays(
                project_root,
                dataset=dataset,
                model=model,
                attack_score_subdir=attack_score_subdir,
            )

            member_pool_size = len(np.asarray(arrays[f"member_{score_names[0]}"]))
            nonmember_pool_size = len(np.asarray(arrays[f"nonmember_{score_names[0]}"]))
            max_size = min(member_pool_size, nonmember_pool_size)

            for sample_size in sample_sizes:
                if sample_size > max_size:
                    for score_name in score_names:
                        skipped.append(
                            {
                                "dataset": dataset,
                                "model": model,
                                "attack_score": score_name,
                                "sample_size": sample_size,
                                "reason": f"sample_size exceeds available balanced pool {max_size}",
                            }
                        )
                    continue

                for repeat in range(n_repeats):
                    member_idx = rng.choice(member_pool_size, size=sample_size, replace=False)
                    nonmember_idx = rng.choice(nonmember_pool_size, size=sample_size, replace=False)

                    for score_name in score_names:
                        member_scores_all = np.asarray(arrays[f"member_{score_name}"], dtype=float)
                        nonmember_scores_all = np.asarray(arrays[f"nonmember_{score_name}"], dtype=float)
                        repeat_rows.extend(
                            sample_metric_rows(
                                dataset=dataset,
                                model=model,
                                score_name=score_name,
                                sample_size=sample_size,
                                repeat=repeat,
                                member_scores=member_scores_all[member_idx],
                                nonmember_scores=nonmember_scores_all[nonmember_idx],
                            )
                        )

    aggregate = aggregate_rows(repeat_rows)
    repeat_path = output_dir / "sample_size_repeats.csv"
    aggregate_path = output_dir / "sample_size_sensitivity.csv"
    skipped_path = output_dir / "sample_size_skipped.csv"
    config_path = output_dir / "subsampling_config.json"
    summary_path = output_dir / "subsampling_summary.md"

    write_csv(repeat_path, repeat_rows)
    write_csv(aggregate_path, aggregate)
    if skipped:
        write_csv(skipped_path, skipped)
    else:
        skipped_path.write_text("dataset,model,attack_score,sample_size,reason\n", encoding="utf-8")

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    config = {
        "generated_at": generated_at,
        "datasets": datasets,
        "models": models,
        "attack_score_subdir": attack_score_subdir,
        "output_dir": str(output_dir.relative_to(project_root)),
        "sample_sizes": list(sample_sizes),
        "n_repeats": n_repeats,
        "random_state": random_state,
        "score_names": list(score_names),
        "metrics": ["AUC", "TPR@1%FPR", "TPR@0.1%FPR", "membership_advantage@1%FPR", "membership_advantage@0.1%FPR"],
        "repeat_path": str(repeat_path.relative_to(project_root)),
        "aggregate_path": str(aggregate_path.relative_to(project_root)),
        "skipped_path": str(skipped_path.relative_to(project_root)),
    }
    write_json(config_path, config)
    summary_path.write_text(subsampling_summary_text(config, aggregate), encoding="utf-8")
    return config


def subsampling_summary_text(config: dict[str, Any], aggregate: list[dict[str, Any]]) -> str:
    auc_rows = [row for row in aggregate if row["metric"] == "AUC"]
    auc_rows = sorted(auc_rows, key=lambda row: (row["dataset"], row["model"], row["attack_score"], row["sample_size"]))

    lines = [
        "# Sample-Size Sensitivity Summary",
        "",
        f"Generated: {config['generated_at']}",
        "",
        "## Configuration",
        "",
        f"- Datasets: `{config['datasets']}`",
        f"- Models: `{config['models']}`",
        f"- Attack score source: `{config['attack_score_subdir']}`",
        f"- Sample sizes: `{config['sample_sizes']}`",
        f"- Repeats per sample size: {config['n_repeats']}",
        "",
        "## Outputs",
        "",
        f"- Repeated subsampling rows: `{config['repeat_path']}`",
        f"- Aggregated sensitivity table: `{config['aggregate_path']}`",
        f"- Skipped sample sizes: `{config['skipped_path']}`",
        "",
        "## AUC Stability Snapshot",
        "",
        "| Dataset | Model | Attack Score | Audit Size | Mean AUC | 95% Width |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in auc_rows[:40]:
        lines.append(
            f"| {row['dataset']} | {row['model']} | {row['attack_score']} | "
            f"{row['sample_size']} | {row['mean']:.4f} | {row['interval_width']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Each repeat samples balanced member and non-member audit subsets without replacement.",
            "- Within each dataset/model/sample-size/repeat, the same sampled rows are reused for every attack score.",
            "- The 95% width is the empirical 97.5th minus 2.5th percentile across repeats.",
            "- Low-FPR metrics use the same tie-aware randomized operating-point convention as the main metric tables.",
            "- Warnings are added when the expected false-positive budget is very small.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_sample_sizes(values: list[str]) -> tuple[int, ...]:
    return tuple(int(value) for value in values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repeated balanced audit sample-size sensitivity analysis.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--datasets", nargs="+", default=list(CORE_DATASETS), choices=list(ALL_DATASETS))
    parser.add_argument("--models", nargs="+", default=list(CORE_MODELS), choices=list(ALL_MODELS))
    parser.add_argument("--attack-score-subdir", default="attack_scores")
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/results/core"))
    parser.add_argument("--sample-sizes", nargs="+", default=[str(value) for value in DEFAULT_SAMPLE_SIZES])
    parser.add_argument("--n-repeats", type=int, default=200)
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir

    config = run_subsampling(
        project_root,
        datasets=args.datasets,
        models=args.models,
        attack_score_subdir=args.attack_score_subdir,
        output_dir=output_dir,
        sample_sizes=parse_sample_sizes(args.sample_sizes),
        n_repeats=args.n_repeats,
        random_state=args.random_state,
    )
    print(f"wrote {config['repeat_path']}")
    print(f"wrote {config['aggregate_path']}")


if __name__ == "__main__":
    main()
