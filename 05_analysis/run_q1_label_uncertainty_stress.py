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
SRC_DIR = PROJECT_ROOT / "05_analysis" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mia_eval.data import DEFAULT_RANDOM_STATE, default_project_root
from mia_eval.experiments import FPR_LEVELS, load_score_arrays, metric_label_for_fpr
from mia_eval.metrics import attack_auc, membership_advantage_at_fpr, operating_point_at_fpr, tpr_at_fpr


DEFAULT_CORRUPTION_RATES = (0.0, 0.005, 0.01, 0.02, 0.05)
DEFAULT_SAMPLE_SIZES = (250, 500, 1000, 2500, 5000, 10000, 15000)


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


def rate_slug(rate: float) -> str:
    return f"{rate:.3f}".replace(".", "p")


def corrupt_membership_labels(
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    *,
    corruption_rate: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    if not 0 <= corruption_rate < 0.5:
        raise ValueError("corruption_rate must be in [0, 0.5)")

    members = np.asarray(member_scores, dtype=float)
    nonmembers = np.asarray(nonmember_scores, dtype=float)
    n_members = len(members)
    n_nonmembers = len(nonmembers)
    n_swap_members = int(round(n_members * corruption_rate))
    n_swap_nonmembers = int(round(n_nonmembers * corruption_rate))

    if n_swap_members == 0 and n_swap_nonmembers == 0:
        return members.copy(), nonmembers.copy(), {
            "n_swap_members_to_nonmember": 0,
            "n_swap_nonmembers_to_member": 0,
            "observed_member_count": int(n_members),
            "observed_nonmember_count": int(n_nonmembers),
        }

    member_swap_idx = rng.choice(n_members, size=n_swap_members, replace=False)
    nonmember_swap_idx = rng.choice(n_nonmembers, size=n_swap_nonmembers, replace=False)
    member_keep = np.ones(n_members, dtype=bool)
    nonmember_keep = np.ones(n_nonmembers, dtype=bool)
    member_keep[member_swap_idx] = False
    nonmember_keep[nonmember_swap_idx] = False

    observed_members = np.concatenate([members[member_keep], nonmembers[nonmember_swap_idx]])
    observed_nonmembers = np.concatenate([nonmembers[nonmember_keep], members[member_swap_idx]])

    return observed_members, observed_nonmembers, {
        "n_swap_members_to_nonmember": int(n_swap_members),
        "n_swap_nonmembers_to_member": int(n_swap_nonmembers),
        "observed_member_count": int(len(observed_members)),
        "observed_nonmember_count": int(len(observed_nonmembers)),
    }


def metric_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    corruption_rate: float,
    repeat: int | str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "dataset": dataset,
            "model": model,
            "attack_score": score_name,
            "corruption_rate": corruption_rate,
            "repeat": repeat,
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
        op = operating_point_at_fpr(member_scores, nonmember_scores, fpr)
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "corruption_rate": corruption_rate,
                "repeat": repeat,
                "metric": metric_label_for_fpr("TPR", fpr),
                "value": float(op["tpr"]),
                "threshold": float(op["threshold"]),
                "empirical_fpr": float(op["fpr"]),
                "tie_fraction": float(op["tie_fraction"]),
                "n_members": int(len(member_scores)),
                "n_nonmembers": int(len(nonmember_scores)),
            }
        )
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "corruption_rate": corruption_rate,
                "repeat": repeat,
                "metric": metric_label_for_fpr("membership_advantage", fpr),
                "value": float(membership_advantage_at_fpr(member_scores, nonmember_scores, fpr)),
                "threshold": float(op["threshold"]),
                "empirical_fpr": float(op["fpr"]),
                "tie_fraction": float(op["tie_fraction"]),
                "n_members": int(len(member_scores)),
                "n_nonmembers": int(len(nonmember_scores)),
            }
        )
    return rows


def aggregate_repeat_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, float, str], list[float]] = {}
    for row in rows:
        key = (
            str(row["dataset"]),
            str(row["model"]),
            str(row["attack_score"]),
            float(row["corruption_rate"]),
            str(row["metric"]),
        )
        groups.setdefault(key, []).append(float(row["value"]))

    out: list[dict[str, Any]] = []
    for (dataset, model, score_name, corruption_rate, metric), values_list in sorted(groups.items()):
        values = np.asarray(values_list, dtype=float)
        out.append(
            {
                "dataset": dataset,
                "model": model,
                "attack_score": score_name,
                "corruption_rate": corruption_rate,
                "metric": metric,
                "n_repeats": int(len(values)),
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                "p025": float(np.quantile(values, 0.025)),
                "median": float(np.quantile(values, 0.5)),
                "p975": float(np.quantile(values, 0.975)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }
        )
    return out


def tail_warning(expected_false_positives: float) -> str:
    if expected_false_positives < 1:
        return "severe_tail_resolution_warning"
    if expected_false_positives < 5:
        return "tail_resolution_warning"
    return ""


def tail_warning_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    corruption_rates: tuple[float, ...],
    sample_sizes: tuple[int, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rate in corruption_rates:
        for sample_size in sample_sizes:
            for fpr in FPR_LEVELS:
                expected = sample_size * fpr
                rows.append(
                    {
                        "dataset": dataset,
                        "model": model,
                        "attack_score": score_name,
                        "corruption_rate": rate,
                        "n_nonmembers": int(sample_size),
                        "target_fpr": fpr,
                        "expected_false_positives": float(expected),
                        "warning": tail_warning(expected),
                    }
                )
    return rows


def run_stress(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    output_dir = (project_root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir
    arrays_dir = output_dir / "score_arrays"
    tables_dir = output_dir / "tables"
    arrays_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    arrays, metadata = load_score_arrays(
        project_root,
        dataset=args.dataset,
        model=args.model,
        attack_score_subdir=args.attack_score_subdir,
    )
    member_scores = np.asarray(arrays[f"member_{args.score_name}"], dtype=float)
    nonmember_scores = np.asarray(arrays[f"nonmember_{args.score_name}"], dtype=float)
    corruption_rates = tuple(args.corruption_rates)

    repeat_rows: list[dict[str, Any]] = []
    canonical_rows: list[dict[str, Any]] = []
    canonical_metadata_rows: list[dict[str, Any]] = []

    for rate_index, rate in enumerate(corruption_rates):
        for repeat in range(args.n_repeats):
            rng = np.random.default_rng(args.random_state + rate_index * 100000 + repeat)
            observed_members, observed_nonmembers, _counts = corrupt_membership_labels(
                member_scores,
                nonmember_scores,
                corruption_rate=rate,
                rng=rng,
            )
            repeat_rows.extend(
                metric_rows(
                    dataset=args.dataset,
                    model=args.model,
                    score_name=args.score_name,
                    corruption_rate=rate,
                    repeat=repeat,
                    member_scores=observed_members,
                    nonmember_scores=observed_nonmembers,
                )
            )

        canonical_rng = np.random.default_rng(args.random_state + rate_index * 100000 + 99999)
        observed_members, observed_nonmembers, counts = corrupt_membership_labels(
            member_scores,
            nonmember_scores,
            corruption_rate=rate,
            rng=canonical_rng,
        )
        slug = rate_slug(rate)
        score_path = arrays_dir / f"neg_loss_label_corruption_{slug}.npz"
        np.savez_compressed(
            score_path,
            member_neg_loss=observed_members.astype(np.float32, copy=False),
            nonmember_neg_loss=observed_nonmembers.astype(np.float32, copy=False),
        )
        canonical_rows.extend(
            metric_rows(
                dataset=args.dataset,
                model=args.model,
                score_name=args.score_name,
                corruption_rate=rate,
                repeat="canonical",
                member_scores=observed_members,
                nonmember_scores=observed_nonmembers,
            )
        )
        canonical_metadata_rows.append(
            {
                "dataset": args.dataset,
                "model": args.model,
                "attack_score": args.score_name,
                "corruption_rate": rate,
                "rate_slug": slug,
                "score_path": str(score_path.relative_to(project_root)),
                "canonical_seed": int(args.random_state + rate_index * 100000 + 99999),
                **counts,
            }
        )

    repeat_path = tables_dir / "label_uncertainty_repeats.csv"
    summary_path = tables_dir / "label_uncertainty_summary.csv"
    canonical_path = tables_dir / "canonical_corruption_metrics.csv"
    canonical_metadata_path = tables_dir / "canonical_score_arrays.csv"
    tail_path = tables_dir / "tail_resolution_warnings.csv"
    config_path = output_dir / "run_config.json"

    write_csv(repeat_path, repeat_rows)
    write_csv(summary_path, aggregate_repeat_rows(repeat_rows))
    write_csv(canonical_path, canonical_rows)
    write_csv(canonical_metadata_path, canonical_metadata_rows)
    write_csv(
        tail_path,
        tail_warning_rows(
            dataset=args.dataset,
            model=args.model,
            score_name=args.score_name,
            corruption_rates=corruption_rates,
            sample_sizes=tuple(args.sample_sizes),
        ),
    )

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    config = {
        "generated_at": generated_at,
        "purpose": "Q1 one-setting audit-label uncertainty stress test.",
        "dataset": args.dataset,
        "model": args.model,
        "attack_score": args.score_name,
        "attack_score_subdir": args.attack_score_subdir,
        "source_metadata": metadata,
        "member_count": int(len(member_scores)),
        "nonmember_count": int(len(nonmember_scores)),
        "corruption_rates": list(corruption_rates),
        "n_repeats": int(args.n_repeats),
        "random_state": int(args.random_state),
        "sample_sizes_for_tail_warnings": list(args.sample_sizes),
        "arrays_dir": str(arrays_dir.relative_to(project_root)),
        "repeat_path": str(repeat_path.relative_to(project_root)),
        "summary_path": str(summary_path.relative_to(project_root)),
        "canonical_metrics_path": str(canonical_path.relative_to(project_root)),
        "canonical_score_arrays_path": str(canonical_metadata_path.relative_to(project_root)),
        "tail_resolution_warnings_path": str(tail_path.relative_to(project_root)),
    }
    write_json(config_path, config)
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded audit-label uncertainty stress test.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--dataset", default="credit_default")
    parser.add_argument("--model", default="random_forest")
    parser.add_argument("--score-name", default="neg_loss")
    parser.add_argument("--attack-score-subdir", default="expanded_tabular_stage1/attack_scores")
    parser.add_argument("--output-dir", type=Path, default=Path("05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss"))
    parser.add_argument("--corruption-rates", nargs="+", type=float, default=list(DEFAULT_CORRUPTION_RATES))
    parser.add_argument("--n-repeats", type=int, default=200)
    parser.add_argument("--sample-sizes", nargs="+", type=int, default=list(DEFAULT_SAMPLE_SIZES))
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    return parser.parse_args()


def main() -> None:
    config = run_stress(parse_args())
    print(f"summary={config['summary_path']}")
    print(f"canonical_score_arrays={config['canonical_score_arrays_path']}")
    print(f"tail_resolution_warnings={config['tail_resolution_warnings_path']}")


if __name__ == "__main__":
    main()
