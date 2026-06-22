from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.data import default_project_root
from mia_eval.experiments import FPR_LEVELS, load_score_arrays, metric_label_for_fpr
from mia_eval.metrics import threshold_at_fpr


DEFAULT_SETTINGS = (
    ("credit_default", "random_forest", "neg_loss", "CD/RF"),
    ("credit_default", "extra_trees", "neg_loss", "CD/ET"),
    ("diabetes_readmission", "random_forest", "neg_loss", "Diab/RF"),
    ("diabetes_readmission", "extra_trees", "neg_loss", "Diab/ET"),
)

DATASET_LABELS = {
    "credit_default": "Credit default",
    "diabetes_readmission": "Diabetes readmission",
}

MODEL_LABELS = {
    "random_forest": "Random forest",
    "extra_trees": "Extra trees",
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


def format_float(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}"


def format_threshold(value: float) -> str:
    return f"{value:.6g}"


def operating_point_rows(
    *,
    dataset: str,
    model: str,
    attack_score: str,
    setting_label: str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    target_fpr: float,
) -> list[dict[str, Any]]:
    threshold = threshold_at_fpr(nonmember_scores, target_fpr)
    members = np.asarray(member_scores, dtype=float)
    nonmembers = np.asarray(nonmember_scores, dtype=float)

    member_gt = int(np.sum(members > threshold))
    member_eq = int(np.sum(members == threshold))
    member_ge = member_gt + member_eq
    nonmember_gt = int(np.sum(nonmembers > threshold))
    nonmember_eq = int(np.sum(nonmembers == threshold))
    nonmember_ge = nonmember_gt + nonmember_eq

    n_members = int(len(members))
    n_nonmembers = int(len(nonmembers))
    nonmember_gt_rate = nonmember_gt / n_nonmembers
    nonmember_eq_rate = nonmember_eq / n_nonmembers
    if nonmember_eq_rate > 0:
        tie_fraction = float(np.clip((target_fpr - nonmember_gt_rate) / nonmember_eq_rate, 0.0, 1.0))
    else:
        tie_fraction = 0.0

    rule_specs = (
        ("strict_gt", "score > threshold", 0.0, member_gt, nonmember_gt),
        ("inclusive_ge", "score >= threshold", 1.0, member_ge, nonmember_ge),
        (
            "randomized_tie_aware",
            "score > threshold plus randomized threshold ties",
            tie_fraction,
            member_gt + tie_fraction * member_eq,
            nonmember_gt + tie_fraction * nonmember_eq,
        ),
    )

    rows: list[dict[str, Any]] = []
    for rule, rule_description, included_tie_fraction, member_positive, nonmember_positive in rule_specs:
        tpr = float(member_positive / n_members)
        fpr = float(nonmember_positive / n_nonmembers)
        rows.append(
            {
                "setting": setting_label,
                "dataset": dataset,
                "dataset_label": DATASET_LABELS.get(dataset, dataset),
                "model": model,
                "model_label": MODEL_LABELS.get(model, model),
                "attack_score": attack_score,
                "target_fpr": float(target_fpr),
                "metric": metric_label_for_fpr("TPR", target_fpr),
                "rule": rule,
                "rule_description": rule_description,
                "threshold": float(threshold),
                "included_tie_fraction": float(included_tie_fraction),
                "tpr": tpr,
                "empirical_fpr": fpr,
                "membership_advantage": float(tpr - fpr),
                "target_fpr_gap": float(fpr - target_fpr),
                "n_members": n_members,
                "n_nonmembers": n_nonmembers,
                "member_gt_threshold": int(member_gt),
                "member_eq_threshold": int(member_eq),
                "member_ge_threshold": int(member_ge),
                "nonmember_gt_threshold": int(nonmember_gt),
                "nonmember_eq_threshold": int(nonmember_eq),
                "nonmember_ge_threshold": int(nonmember_ge),
                "nonmember_tie_rate": float(nonmember_eq_rate),
            }
        )
    return rows


def make_paper_rows(long_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, float], dict[str, dict[str, Any]]] = {}
    for row in long_rows:
        key = (
            str(row["dataset"]),
            str(row["model"]),
            str(row["attack_score"]),
            float(row["target_fpr"]),
        )
        grouped.setdefault(key, {})[str(row["rule"])] = row

    setting_order = {
        (dataset, model, score_name): idx
        for idx, (dataset, model, score_name, _label) in enumerate(DEFAULT_SETTINGS)
    }
    fpr_order = {0.01: 0, 0.001: 1}

    paper_rows: list[dict[str, Any]] = []
    for key, by_rule in sorted(
        grouped.items(),
        key=lambda item: (
            setting_order.get((item[0][0], item[0][1], item[0][2]), len(setting_order)),
            fpr_order.get(item[0][3], len(fpr_order)),
        ),
    ):
        dataset, model, attack_score, target_fpr = key
        strict = by_rule["strict_gt"]
        inclusive = by_rule["inclusive_ge"]
        randomized = by_rule["randomized_tie_aware"]
        paper_rows.append(
            {
                "setting": randomized["setting"],
                "dataset": dataset,
                "model": model,
                "attack_score": attack_score,
                "target_fpr": target_fpr,
                "threshold": randomized["threshold"],
                "tie_fraction": randomized["included_tie_fraction"],
                "strict_tpr": strict["tpr"],
                "randomized_tpr": randomized["tpr"],
                "inclusive_tpr": inclusive["tpr"],
                "strict_fpr": strict["empirical_fpr"],
                "randomized_fpr": randomized["empirical_fpr"],
                "inclusive_fpr": inclusive["empirical_fpr"],
                "tpr_strict_to_inclusive_width": float(inclusive["tpr"] - strict["tpr"]),
                "fpr_strict_to_inclusive_width": float(inclusive["empirical_fpr"] - strict["empirical_fpr"]),
                "member_ties_at_threshold": randomized["member_eq_threshold"],
                "nonmember_ties_at_threshold": randomized["nonmember_eq_threshold"],
                "n_members": randomized["n_members"],
                "n_nonmembers": randomized["n_nonmembers"],
            }
        )
    return paper_rows


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Setting | Target FPR | Threshold | Tie frac. | Strict TPR/FPR | Randomized TPR/FPR | Inclusive TPR/FPR |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {setting} | {target_fpr} | {threshold} | {tie_fraction} | {strict_pair} | {randomized_pair} | {inclusive_pair} |".format(
                setting=row["setting"],
                target_fpr="1%" if float(row["target_fpr"]) == 0.01 else "0.1%",
                threshold=format_threshold(float(row["threshold"])),
                tie_fraction=format_float(float(row["tie_fraction"]), 3),
                strict_pair=f"{format_float(float(row['strict_tpr']))}/{format_float(float(row['strict_fpr']))}",
                randomized_pair=f"{format_float(float(row['randomized_tpr']))}/{format_float(float(row['randomized_fpr']))}",
                inclusive_pair=f"{format_float(float(row['inclusive_tpr']))}/{format_float(float(row['inclusive_fpr']))}",
            )
        )
    return "\n".join(lines)


def write_summary(path: Path, paper_rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    max_tpr_width = max(float(row["tpr_strict_to_inclusive_width"]) for row in paper_rows)
    max_fpr_width = max(float(row["fpr_strict_to_inclusive_width"]) for row in paper_rows)
    max_width_row = max(paper_rows, key=lambda row: float(row["tpr_strict_to_inclusive_width"]))
    paper_table_rows = [
        row
        for row in paper_rows
        if float(row["target_fpr"]) in {0.01, 0.001}
    ]

    lines = [
        "# Q1 Tie-Rule Sensitivity",
        "",
        "This sensitivity analysis compares three low-FPR operating rules using the existing expanded Stage1 negative-loss score arrays:",
        "",
        "- Strict: scores are positive only when `score > threshold`.",
        "- Inclusive: scores are positive when `score >= threshold`.",
        "- Randomized tie-aware: scores above threshold are positive, and threshold ties are included with the fraction needed to match the target FPR in expectation.",
        "",
        "The threshold is the existing Stage1 non-member tail threshold, `np.quantile(nonmember_scores, 1 - target_fpr, method=\"higher\")`.",
        "",
        "## Paper-ready table",
        "",
        markdown_table(paper_table_rows),
        "",
        "## Key readout",
        "",
        f"- Maximum strict-to-inclusive TPR width: {format_float(max_tpr_width)} ({max_width_row['setting']} at {format_float(float(max_width_row['target_fpr']) * 100, 1)}% FPR).",
        f"- Maximum strict-to-inclusive FPR width: {format_float(max_fpr_width)}.",
        "- The randomized tie-aware column reproduces the intended low-FPR convention by keeping empirical FPR at the target in expectation.",
        "",
        "## Outputs",
        "",
        f"- Long CSV: `{config['long_csv_path']}`",
        f"- Paper table CSV: `{config['paper_table_csv_path']}`",
        f"- Run config: `{config['run_config_path']}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def run_sensitivity(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    output_dir = (project_root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    long_rows: list[dict[str, Any]] = []
    source_metadata: dict[str, Any] = {}
    for dataset, model, score_name, setting_label in DEFAULT_SETTINGS:
        arrays, metadata = load_score_arrays(
            project_root,
            dataset=dataset,
            model=model,
            attack_score_subdir=args.attack_score_subdir,
        )
        member_scores = np.asarray(arrays[f"member_{score_name}"], dtype=float)
        nonmember_scores = np.asarray(arrays[f"nonmember_{score_name}"], dtype=float)
        source_metadata[f"{dataset}/{model}/{score_name}"] = metadata
        for target_fpr in args.fpr_levels:
            long_rows.extend(
                operating_point_rows(
                    dataset=dataset,
                    model=model,
                    attack_score=score_name,
                    setting_label=setting_label,
                    member_scores=member_scores,
                    nonmember_scores=nonmember_scores,
                    target_fpr=float(target_fpr),
                )
            )

    paper_rows = make_paper_rows(long_rows)

    long_csv_path = output_dir / "tie_rule_operating_points.csv"
    paper_table_csv_path = output_dir / "paper_table_tie_rule_sensitivity.csv"
    summary_path = output_dir / "q1_tie_rule_sensitivity_summary.md"
    run_config_path = output_dir / "run_config.json"

    write_csv(long_csv_path, long_rows)
    write_csv(paper_table_csv_path, paper_rows)

    config = {
        "purpose": "Q1 low-FPR tie-rule sensitivity for negative-loss score arrays.",
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "attack_score_subdir": args.attack_score_subdir,
        "settings": [
            {"dataset": dataset, "model": model, "attack_score": score_name, "label": label}
            for dataset, model, score_name, label in DEFAULT_SETTINGS
        ],
        "fpr_levels": [float(value) for value in args.fpr_levels],
        "source_metadata": source_metadata,
        "long_csv_path": str(long_csv_path.relative_to(project_root)),
        "paper_table_csv_path": str(paper_table_csv_path.relative_to(project_root)),
        "summary_path": str(summary_path.relative_to(project_root)),
        "run_config_path": str(run_config_path.relative_to(project_root)),
    }
    write_json(run_config_path, config)
    write_summary(summary_path, paper_rows, config)
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare strict, inclusive, and randomized tie-aware low-FPR rules.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--attack-score-subdir", default="expanded_tabular_stage1/attack_scores")
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/results/q1_tie_rule_sensitivity"))
    parser.add_argument("--fpr-levels", nargs="+", type=float, default=list(FPR_LEVELS))
    return parser.parse_args()


def main() -> None:
    config = run_sensitivity(parse_args())
    print(f"long_csv={config['long_csv_path']}")
    print(f"paper_table_csv={config['paper_table_csv_path']}")
    print(f"summary={config['summary_path']}")


if __name__ == "__main__":
    main()
