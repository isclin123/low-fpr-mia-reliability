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
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.bootstrap import stratified_bootstrap_ci
from mia_eval.data import DEFAULT_RANDOM_STATE
from mia_eval.experiments import load_score_arrays, metric_label_for_fpr
from mia_eval.metrics import attack_auc, tpr_at_fpr


FPR_LEVELS = (0.01, 0.001)


def auc_group_ids(member_scores: Any, nonmember_scores: Any) -> tuple[Any, Any, int]:
    """Map each fixed score to a tie group for exact weighted AUC bootstrap."""
    import numpy as np

    member_scores = np.asarray(member_scores, dtype=float)
    nonmember_scores = np.asarray(nonmember_scores, dtype=float)
    all_scores = np.concatenate([member_scores, nonmember_scores])
    order = np.argsort(all_scores, kind="mergesort")
    sorted_scores = all_scores[order]
    group_starts = np.empty(len(sorted_scores), dtype=bool)
    group_starts[0] = True
    group_starts[1:] = sorted_scores[1:] != sorted_scores[:-1]
    group_ids_sorted = np.cumsum(group_starts) - 1
    group_ids = np.empty_like(group_ids_sorted)
    group_ids[order] = group_ids_sorted
    n_member = len(member_scores)
    n_groups = int(group_ids_sorted[-1]) + 1
    return group_ids[:n_member], group_ids[n_member:], n_groups


def weighted_auc_from_group_weights(member_group_weights: Any, nonmember_group_weights: Any) -> float:
    import numpy as np

    nonmember_below = np.cumsum(nonmember_group_weights) - nonmember_group_weights
    numerator = np.sum(member_group_weights * (nonmember_below + 0.5 * nonmember_group_weights))
    denominator = float(np.sum(member_group_weights) * np.sum(nonmember_group_weights))
    return float(numerator / denominator)


def fast_auc_bootstrap_ci(
    member_scores: Any,
    nonmember_scores: Any,
    *,
    n_bootstrap: int,
    confidence: float,
    random_state: int,
) -> tuple[float, float, float]:
    """Exact stratified bootstrap AUC using one fixed sort and bootstrap weights."""
    import numpy as np

    member_scores = np.asarray(member_scores, dtype=float)
    nonmember_scores = np.asarray(nonmember_scores, dtype=float)
    member_group_ids, nonmember_group_ids, n_groups = auc_group_ids(member_scores, nonmember_scores)
    n_members = len(member_scores)
    n_nonmembers = len(nonmember_scores)

    member_group_weights = np.bincount(member_group_ids, minlength=n_groups).astype(float)
    nonmember_group_weights = np.bincount(nonmember_group_ids, minlength=n_groups).astype(float)
    point = weighted_auc_from_group_weights(member_group_weights, nonmember_group_weights)

    rng = np.random.default_rng(random_state)
    estimates = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        member_idx = rng.integers(0, n_members, n_members)
        nonmember_idx = rng.integers(0, n_nonmembers, n_nonmembers)
        member_counts = np.bincount(member_idx, minlength=n_members)
        nonmember_counts = np.bincount(nonmember_idx, minlength=n_nonmembers)
        member_group_weights = np.bincount(member_group_ids, weights=member_counts, minlength=n_groups)
        nonmember_group_weights = np.bincount(nonmember_group_ids, weights=nonmember_counts, minlength=n_groups)
        estimates[i] = weighted_auc_from_group_weights(member_group_weights, nonmember_group_weights)

    alpha = 1.0 - confidence
    lower, upper = np.quantile(estimates, [alpha / 2.0, 1.0 - alpha / 2.0])
    return point, float(lower), float(upper)


def resolve_path(path: Path, project_root: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root / path


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_summary_rows(summary_csv: Path) -> list[dict[str, str]]:
    df = pd.read_csv(summary_csv)
    required = {"dataset", "model", "best_auc_score"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {summary_csv}: {sorted(missing)}")
    return df[["dataset", "model", "best_auc_score"]].to_dict(orient="records")


def selected_score_rows(summary_csv: Path) -> list[dict[str, str]]:
    rows = []
    for row in read_summary_rows(summary_csv):
        roles_by_score: dict[str, list[str]] = {}
        roles_by_score.setdefault(str(row["best_auc_score"]), []).append("best_auc_score")
        roles_by_score.setdefault("neg_loss", []).append("canonical_neg_loss")
        for score_name, roles in sorted(roles_by_score.items()):
            rows.append(
                {
                    "dataset": str(row["dataset"]),
                    "model": str(row["model"]),
                    "attack_score": score_name,
                    "score_role": ";".join(roles),
                }
            )
    return rows


def metric_functions() -> list[tuple[str, Any]]:
    functions: list[tuple[str, Any]] = [("AUC", attack_auc)]
    for fpr in FPR_LEVELS:
        metric_name = metric_label_for_fpr("TPR", fpr)
        functions.append((metric_name, lambda members, nonmembers, fpr=fpr: tpr_at_fpr(members, nonmembers, fpr)))
    return functions


def harden_ci_rows(
    *,
    project_root: Path,
    selected_scores: list[dict[str, str]],
    attack_score_subdir: str,
    n_bootstrap: int,
    confidence: float,
    random_state: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    metric_specs = metric_functions()
    total = len(selected_scores) * len(metric_specs)
    completed = 0
    for selected_index, selected in enumerate(selected_scores):
        arrays, _metadata = load_score_arrays(
            project_root,
            dataset=selected["dataset"],
            model=selected["model"],
            attack_score_subdir=attack_score_subdir,
        )
        score_name = selected["attack_score"]
        member_scores = arrays[f"member_{score_name}"]
        nonmember_scores = arrays[f"nonmember_{score_name}"]
        for metric_index, (metric_name, metric_fn) in enumerate(metric_specs):
            completed += 1
            seed = random_state + selected_index * 100 + metric_index
            print(
                f"[{completed}/{total}] {selected['dataset']} / {selected['model']} / "
                f"{score_name} / {metric_name}",
                flush=True,
            )
            if metric_name == "AUC":
                point, lower, upper = fast_auc_bootstrap_ci(
                    member_scores,
                    nonmember_scores,
                    n_bootstrap=n_bootstrap,
                    confidence=confidence,
                    random_state=seed,
                )
            else:
                point, lower, upper = stratified_bootstrap_ci(
                    member_scores,
                    nonmember_scores,
                    metric_fn,
                    n_bootstrap=n_bootstrap,
                    confidence=confidence,
                    random_state=seed,
                )
            rows.append(
                {
                    "dataset": selected["dataset"],
                    "model": selected["model"],
                    "attack_score": score_name,
                    "score_role": selected["score_role"],
                    "metric": metric_name,
                    "point": point,
                    "ci_lower": lower,
                    "ci_upper": upper,
                    "ci_width": upper - lower,
                    "confidence": confidence,
                    "n_bootstrap": n_bootstrap,
                    "random_state": seed,
                    "n_members": int(len(member_scores)),
                    "n_nonmembers": int(len(nonmember_scores)),
                }
            )
    return rows


def stage1_comparison_rows(
    *,
    hardening_rows: list[dict[str, Any]],
    stage1_ci_csv: Path,
) -> list[dict[str, Any]]:
    stage1 = pd.read_csv(stage1_ci_csv)
    hard = pd.DataFrame(hardening_rows)
    key_cols = ["dataset", "model", "attack_score", "metric"]
    merged = hard.merge(
        stage1[key_cols + ["point", "ci_lower", "ci_upper", "ci_width", "n_bootstrap"]],
        on=key_cols,
        how="left",
        suffixes=("_hardened", "_stage1"),
    )
    stage1_width = merged["ci_width_stage1"]
    hardened_width = merged["ci_width_hardened"]
    merged["ci_width_ratio_hardened_over_stage1"] = np.where(
        stage1_width == 0,
        np.where(hardened_width == 0, 1.0, np.inf),
        hardened_width / stage1_width,
    )
    return merged.to_dict(orient="records")


def summary_text(config: dict[str, Any], selected_scores: list[dict[str, str]], rows: list[dict[str, Any]], timings: dict[str, float]) -> str:
    metrics = sorted({row["metric"] for row in rows})
    datasets = sorted({row["dataset"] for row in rows})
    models = sorted({row["model"] for row in rows})
    lines = [
        "# Final CI Hardening Summary",
        "",
        f"Generated: {config['generated_at']}",
        "",
        "## Scope",
        "",
        f"- Source run: `{config['source_run_name']}`",
        f"- Attack-score subdir: `{config['attack_score_subdir']}`",
        f"- Summary CSV used for row selection: `{config['summary_csv']}`",
        f"- Output directory: `{config['output_dir']}`",
        f"- Datasets: `{datasets}`",
        f"- Models: `{models}`",
        f"- Selected score rows: `{len(selected_scores)}`",
        f"- Hardened CI rows: `{len(rows)}`",
        f"- Metrics: `{metrics}`",
        "",
        "## Bootstrap Settings",
        "",
        f"- Bootstrap repeats: `{config['n_bootstrap']}`",
        f"- Confidence level: `{config['confidence']}`",
        f"- Random state base: `{config['random_state']}`",
        "",
        "## Outputs",
        "",
        f"- Selected score rows: `{config['selected_scores_path']}`",
        f"- Hardened intervals: `{config['hardened_intervals_path']}`",
        f"- Stage1 comparison: `{config['stage1_comparison_path']}`",
        f"- Run config: `{config['run_config_path']}`",
        "",
        "## Interpretation Boundary",
        "",
        "- This hardening targets main-table candidate rows, not every score/metric in the expanded stage1 grid.",
        "- Selected scores include each dataset/model's best-AUC score and the canonical negative-loss score.",
        "- The hardened rows support final Results v2 wording for AUC and low-FPR TPR intervals.",
        "- AUC intervals use an exact pre-sorted weighted bootstrap implementation to avoid repeated score sorting on large datasets.",
        "",
        "## Timings",
        "",
        "| Stage | Seconds |",
        "|---|---:|",
    ]
    for stage, seconds in timings.items():
        lines.append(f"| {stage} | {seconds:.2f} |")
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    output_dir = resolve_path(args.output_dir, project_root)
    summary_csv = resolve_path(args.summary_csv, project_root)
    stage1_ci_csv = resolve_path(args.stage1_ci_csv, project_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    timings: dict[str, float] = {}
    start = time.perf_counter()
    selected_scores = selected_score_rows(summary_csv)
    timings["select_rows"] = time.perf_counter() - start

    start = time.perf_counter()
    rows = harden_ci_rows(
        project_root=project_root,
        selected_scores=selected_scores,
        attack_score_subdir=args.attack_score_subdir,
        n_bootstrap=args.n_bootstrap,
        confidence=args.confidence,
        random_state=args.random_state,
    )
    timings["bootstrap_hardening"] = time.perf_counter() - start

    selected_scores_path = output_dir / "selected_score_rows.csv"
    hardened_intervals_path = output_dir / "hardened_confidence_intervals.csv"
    stage1_comparison_path = output_dir / "stage1_vs_hardened_confidence_intervals.csv"
    run_config_path = output_dir / "run_config.json"
    summary_path = output_dir / "hardening_summary.md"

    write_csv(selected_scores_path, selected_scores)
    write_csv(hardened_intervals_path, rows)

    comparison_rows = stage1_comparison_rows(hardening_rows=rows, stage1_ci_csv=stage1_ci_csv)
    write_csv(stage1_comparison_path, comparison_rows)

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    config = {
        "generated_at": generated_at,
        "source_run_name": args.source_run_name,
        "attack_score_subdir": args.attack_score_subdir,
        "summary_csv": str(summary_csv.relative_to(project_root)),
        "stage1_ci_csv": str(stage1_ci_csv.relative_to(project_root)),
        "output_dir": str(output_dir.relative_to(project_root)),
        "n_bootstrap": args.n_bootstrap,
        "confidence": args.confidence,
        "random_state": args.random_state,
        "selected_scores_path": str(selected_scores_path.relative_to(project_root)),
        "hardened_intervals_path": str(hardened_intervals_path.relative_to(project_root)),
        "stage1_comparison_path": str(stage1_comparison_path.relative_to(project_root)),
        "run_config_path": str(run_config_path.relative_to(project_root)),
        "summary_path": str(summary_path.relative_to(project_root)),
    }
    write_json(run_config_path, config)
    summary_path.write_text(summary_text(config, selected_scores, rows, timings), encoding="utf-8")
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run focused final CI hardening for main-table MIA rows.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--source-run-name", default="expanded_tabular_stage1")
    parser.add_argument("--attack-score-subdir", default="expanded_tabular_stage1/attack_scores")
    parser.add_argument("--summary-csv", type=Path, default=Path("figures_tables/expanded/expanded_model_comparison_summary.csv"))
    parser.add_argument(
        "--stage1-ci-csv",
        type=Path,
        default=Path("analysis/results/expanded_tabular_stage1/metrics/confidence_intervals.csv"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/results/final_ci_hardening"))
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE + 1)
    return parser.parse_args()


def main() -> None:
    config = run(parse_args())
    print(f"wrote {config['summary_path']}")
    print(f"hardened_intervals={config['hardened_intervals_path']}")


if __name__ == "__main__":
    main()
