from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from mia_eval.attacks import SCORE_NAMES
from mia_eval.bootstrap import stratified_bootstrap_ci
from mia_eval.data import DEFAULT_RANDOM_STATE, default_project_root
from mia_eval.metrics import attack_auc, membership_advantage_at_fpr, operating_point_at_fpr, tpr_at_fpr
from mia_eval.models import ALL_DATASETS, ALL_MODELS, CORE_DATASETS, CORE_MODELS


FPR_LEVELS = (0.01, 0.001)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def metric_label_for_fpr(prefix: str, fpr: float) -> str:
    if fpr == 0.01:
        return f"{prefix}@1%FPR"
    if fpr == 0.001:
        return f"{prefix}@0.1%FPR"
    return f"{prefix}@{fpr:g}FPR"


def advantage_at_fpr(member_scores: np.ndarray, nonmember_scores: np.ndarray, fpr: float) -> float:
    return membership_advantage_at_fpr(member_scores, nonmember_scores, fpr)


def point_metric_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "dataset": dataset,
            "model": model,
            "attack_score": score_name,
            "metric": "AUC",
            "value": float(attack_auc(member_scores, nonmember_scores)),
            "threshold": "",
            "empirical_fpr": "",
            "tie_fraction": "",
            "n_members": int(len(member_scores)),
            "n_nonmembers": int(len(nonmember_scores)),
        }
    ]

    for fpr in FPR_LEVELS:
        operating_point = operating_point_at_fpr(member_scores, nonmember_scores, fpr)
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "metric": metric_label_for_fpr("TPR", fpr),
                "value": operating_point["tpr"],
                "threshold": operating_point["threshold"],
                "empirical_fpr": operating_point["fpr"],
                "tie_fraction": operating_point["tie_fraction"],
                "n_members": int(len(member_scores)),
                "n_nonmembers": int(len(nonmember_scores)),
            }
        )
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "metric": metric_label_for_fpr("membership_advantage", fpr),
                "value": operating_point["membership_advantage"],
                "threshold": operating_point["threshold"],
                "empirical_fpr": operating_point["fpr"],
                "tie_fraction": operating_point["tie_fraction"],
                "n_members": int(len(member_scores)),
                "n_nonmembers": int(len(nonmember_scores)),
            }
        )
    return rows


def ci_metric_functions() -> list[tuple[str, Callable[[np.ndarray, np.ndarray], float]]]:
    functions: list[tuple[str, Callable[[np.ndarray, np.ndarray], float]]] = [("AUC", attack_auc)]
    for fpr in FPR_LEVELS:
        functions.append((metric_label_for_fpr("TPR", fpr), lambda m, n, fpr=fpr: tpr_at_fpr(m, n, fpr)))
        functions.append(
            (
                metric_label_for_fpr("membership_advantage", fpr),
                lambda m, n, fpr=fpr: advantage_at_fpr(m, n, fpr),
            )
        )
    return functions


def confidence_interval_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    n_bootstrap: int,
    confidence: float,
    random_state: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset, (metric_name, metric_fn) in enumerate(ci_metric_functions()):
        point, lower, upper = stratified_bootstrap_ci(
            member_scores,
            nonmember_scores,
            metric_fn,
            n_bootstrap=n_bootstrap,
            confidence=confidence,
            random_state=random_state + offset,
        )
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "metric": metric_name,
                "point": point,
                "ci_lower": lower,
                "ci_upper": upper,
                "ci_width": upper - lower,
                "confidence": confidence,
                "n_bootstrap": n_bootstrap,
                "n_members": int(len(member_scores)),
                "n_nonmembers": int(len(nonmember_scores)),
            }
        )
    return rows


def load_score_arrays(
    project_root: Path,
    *,
    dataset: str,
    model: str,
    attack_score_subdir: str,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    score_dir = project_root / "analysis" / "results" / attack_score_subdir / dataset / model
    score_path = score_dir / "attack_scores.npz"
    metadata_path = score_dir / "metadata.json"
    if not score_path.exists():
        raise FileNotFoundError(f"Missing attack score file: {score_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing attack score metadata: {metadata_path}")
    scores = np.load(score_path)
    arrays = {key: scores[key] for key in scores.files}
    return arrays, read_json(metadata_path)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_metric_tables(
    project_root: Path,
    *,
    datasets: list[str],
    models: list[str],
    attack_score_subdir: str,
    output_dir: Path,
    score_names: tuple[str, ...] = SCORE_NAMES,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    main_rows: list[dict[str, Any]] = []
    ci_rows: list[dict[str, Any]] = []

    for dataset in datasets:
        for model in models:
            arrays, _metadata = load_score_arrays(
                project_root,
                dataset=dataset,
                model=model,
                attack_score_subdir=attack_score_subdir,
            )
            for score_name in score_names:
                member_scores = np.asarray(arrays[f"member_{score_name}"], dtype=float)
                nonmember_scores = np.asarray(arrays[f"nonmember_{score_name}"], dtype=float)

                main_rows.extend(
                    point_metric_rows(
                        dataset=dataset,
                        model=model,
                        score_name=score_name,
                        member_scores=member_scores,
                        nonmember_scores=nonmember_scores,
                    )
                )
                ci_rows.extend(
                    confidence_interval_rows(
                        dataset=dataset,
                        model=model,
                        score_name=score_name,
                        member_scores=member_scores,
                        nonmember_scores=nonmember_scores,
                        n_bootstrap=n_bootstrap,
                        confidence=confidence,
                        random_state=random_state,
                    )
                )

    main_path = output_dir / "main_metrics.csv"
    ci_path = output_dir / "confidence_intervals.csv"
    config_path = output_dir / "run_config.json"
    summary_path = output_dir / "experiment_summary.md"

    write_csv(main_path, main_rows)
    write_csv(ci_path, ci_rows)

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    config = {
        "generated_at": generated_at,
        "datasets": datasets,
        "models": models,
        "attack_score_subdir": attack_score_subdir,
        "output_dir": str(output_dir.relative_to(project_root)),
        "score_names": list(score_names),
        "metrics": ["AUC", "TPR@1%FPR", "TPR@0.1%FPR", "membership_advantage@1%FPR", "membership_advantage@0.1%FPR"],
        "fpr_levels": list(FPR_LEVELS),
        "n_bootstrap": n_bootstrap,
        "confidence": confidence,
        "random_state": random_state,
        "main_metrics_path": str(main_path.relative_to(project_root)),
        "confidence_intervals_path": str(ci_path.relative_to(project_root)),
    }
    write_json(config_path, config)
    summary_path.write_text(experiment_summary_text(config, main_rows, ci_rows), encoding="utf-8")
    return config


def experiment_summary_text(
    config: dict[str, Any],
    main_rows: list[dict[str, Any]],
    ci_rows: list[dict[str, Any]],
) -> str:
    best_auc_rows = [row for row in main_rows if row["metric"] == "AUC"]
    best_auc_rows = sorted(best_auc_rows, key=lambda row: row["value"], reverse=True)
    lines = [
        "# Metric Table Summary",
        "",
        f"Generated: {config['generated_at']}",
        "",
        "## Configuration",
        "",
        f"- Datasets: `{config['datasets']}`",
        f"- Models: `{config['models']}`",
        f"- Attack score source: `{config['attack_score_subdir']}`",
        f"- Bootstrap repeats: {config['n_bootstrap']}",
        f"- Confidence: {config['confidence']}",
        "",
        "## Outputs",
        "",
        f"- Main metrics: `{config['main_metrics_path']}`",
        f"- Confidence intervals: `{config['confidence_intervals_path']}`",
        "",
        "## Highest Smoke/Core AUC Rows",
        "",
        "| Dataset | Model | Attack Score | AUC |",
        "| --- | --- | --- | --- |",
    ]
    for row in best_auc_rows[:10]:
        lines.append(f"| {row['dataset']} | {row['model']} | {row['attack_score']} | {row['value']:.4f} |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Larger attack scores are interpreted as more member-like.",
            "- Low-FPR thresholds are estimated from non-member score tails.",
            "- Ties at the low-FPR threshold use randomized tie-breaking, so reported TPR/FPR values are expected operating-point values rather than all-ties-included values.",
            "- Bootstrap intervals resample member and non-member scores separately.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate MIA metric and confidence interval tables.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--datasets", nargs="+", default=list(CORE_DATASETS), choices=list(ALL_DATASETS))
    parser.add_argument("--models", nargs="+", default=list(CORE_MODELS), choices=list(ALL_MODELS))
    parser.add_argument("--attack-score-subdir", default="attack_scores")
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/results/core"))
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir

    config = run_metric_tables(
        project_root,
        datasets=args.datasets,
        models=args.models,
        attack_score_subdir=args.attack_score_subdir,
        output_dir=output_dir,
        n_bootstrap=args.n_bootstrap,
        confidence=args.confidence,
        random_state=args.random_state,
    )
    print(f"wrote {config['main_metrics_path']}")
    print(f"wrote {config['confidence_intervals_path']}")


if __name__ == "__main__":
    main()
