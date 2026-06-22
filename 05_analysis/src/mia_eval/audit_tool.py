from __future__ import annotations

import csv
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

from mia_eval.attacks import SCORE_NAMES
from mia_eval.bootstrap import stratified_bootstrap_ci
from mia_eval.data import DEFAULT_RANDOM_STATE
from mia_eval.experiments import FPR_LEVELS, metric_label_for_fpr
from mia_eval.intervals import fixed_threshold_tpr_wilson_interval
from mia_eval.metrics import attack_auc, membership_advantage_at_fpr, operating_point_at_fpr, tpr_at_fpr
from mia_eval.subsampling import DEFAULT_SAMPLE_SIZES


@dataclass(frozen=True)
class AuditToolConfig:
    input_path: Path
    input_format: str
    output_dir: Path
    score_names: tuple[str, ...] = SCORE_NAMES
    dataset: str = ""
    model: str = ""
    fpr_levels: tuple[float, ...] = FPR_LEVELS
    n_bootstrap: int = 1000
    confidence: float = 0.95
    n_repeats: int = 200
    sample_sizes: tuple[int, ...] = DEFAULT_SAMPLE_SIZES
    random_state: int = DEFAULT_RANDOM_STATE
    membership_column: str = "membership"
    sample_id_column: str = "sample_id"
    make_figures: bool = True


@dataclass(frozen=True)
class AuditScores:
    score_names: tuple[str, ...]
    member_scores: dict[str, np.ndarray]
    nonmember_scores: dict[str, np.ndarray]
    metadata: dict[str, Any]


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


def clean_scores(values: Any, *, key: str) -> np.ndarray:
    scores = np.asarray(values, dtype=float)
    if scores.ndim != 1:
        raise ValueError(f"{key} must be a one-dimensional score array")
    if len(scores) == 0:
        raise ValueError(f"{key} must be non-empty")
    if not np.all(np.isfinite(scores)):
        raise ValueError(f"{key} contains NaN or infinite values")
    return scores


def infer_npz_score_names(keys: list[str]) -> tuple[str, ...]:
    ignored = {"idx", "ids", "labels"}
    names: list[str] = []
    for key in sorted(keys):
        if not key.startswith("member_"):
            continue
        score_name = key.removeprefix("member_")
        if score_name in ignored:
            continue
        if f"nonmember_{score_name}" in keys:
            names.append(score_name)
    if not names:
        raise ValueError("Could not infer score names from NPZ keys")
    return tuple(names)


def validate_common_lengths(scores: AuditScores) -> None:
    member_lengths = {len(values) for values in scores.member_scores.values()}
    nonmember_lengths = {len(values) for values in scores.nonmember_scores.values()}
    if len(member_lengths) != 1:
        raise ValueError("All member score arrays must have the same length")
    if len(nonmember_lengths) != 1:
        raise ValueError("All non-member score arrays must have the same length")


def load_npz_scores(input_path: Path, score_names: tuple[str, ...]) -> AuditScores:
    loaded = np.load(input_path)
    keys = list(loaded.files)
    resolved_score_names = score_names or infer_npz_score_names(keys)

    member_scores: dict[str, np.ndarray] = {}
    nonmember_scores: dict[str, np.ndarray] = {}
    for score_name in resolved_score_names:
        member_key = f"member_{score_name}"
        nonmember_key = f"nonmember_{score_name}"
        if member_key not in loaded.files:
            raise ValueError(f"Missing NPZ key: {member_key}")
        if nonmember_key not in loaded.files:
            raise ValueError(f"Missing NPZ key: {nonmember_key}")
        member_scores[score_name] = clean_scores(loaded[member_key], key=member_key)
        nonmember_scores[score_name] = clean_scores(loaded[nonmember_key], key=nonmember_key)

    scores = AuditScores(
        score_names=tuple(resolved_score_names),
        member_scores=member_scores,
        nonmember_scores=nonmember_scores,
        metadata={
            "input_format": "npz",
            "input_path": str(input_path),
            "npz_keys": keys,
        },
    )
    validate_common_lengths(scores)
    return scores


def membership_mask(values: pd.Series) -> np.ndarray:
    if pd.api.types.is_numeric_dtype(values):
        unique = set(values.dropna().astype(int).tolist())
        if not unique.issubset({0, 1}):
            raise ValueError("Numeric membership column must contain only 0 and 1")
        return values.astype(int).to_numpy() == 1

    normalized = values.astype(str).str.strip().str.lower()
    truthy = {"1", "true", "t", "yes", "y", "member", "members", "train"}
    falsy = {"0", "false", "f", "no", "n", "nonmember", "non-member", "non_member", "test"}
    unknown = set(normalized.unique()) - truthy - falsy
    if unknown:
        raise ValueError(f"Unsupported membership values: {sorted(unknown)}")
    return normalized.isin(truthy).to_numpy()


def infer_csv_score_names(frame: pd.DataFrame, membership_column: str, sample_id_column: str) -> tuple[str, ...]:
    excluded = {membership_column, sample_id_column, "dataset", "model", "label", "split"}
    names = [
        column
        for column in frame.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(frame[column])
    ]
    if not names:
        raise ValueError("Could not infer score columns from CSV")
    return tuple(names)


def unique_column_value(frame: pd.DataFrame, column: str) -> str | None:
    if column not in frame.columns:
        return None
    values = [str(value) for value in frame[column].dropna().unique()]
    if len(values) == 1:
        return values[0]
    return None


def load_csv_scores(
    input_path: Path,
    score_names: tuple[str, ...],
    *,
    membership_column: str,
    sample_id_column: str,
) -> AuditScores:
    frame = pd.read_csv(input_path)
    if membership_column not in frame.columns:
        raise ValueError(f"Missing membership column: {membership_column}")

    resolved_score_names = score_names or infer_csv_score_names(frame, membership_column, sample_id_column)
    missing = [name for name in resolved_score_names if name not in frame.columns]
    if missing:
        raise ValueError(f"Missing score columns: {missing}")

    member_mask = membership_mask(frame[membership_column])
    nonmember_mask = ~member_mask
    if not np.any(member_mask) or not np.any(nonmember_mask):
        raise ValueError("CSV must contain at least one member and one non-member row")

    member_scores: dict[str, np.ndarray] = {}
    nonmember_scores: dict[str, np.ndarray] = {}
    for score_name in resolved_score_names:
        member_scores[score_name] = clean_scores(frame.loc[member_mask, score_name].to_numpy(), key=f"member_{score_name}")
        nonmember_scores[score_name] = clean_scores(
            frame.loc[nonmember_mask, score_name].to_numpy(),
            key=f"nonmember_{score_name}",
        )

    scores = AuditScores(
        score_names=tuple(resolved_score_names),
        member_scores=member_scores,
        nonmember_scores=nonmember_scores,
        metadata={
            "input_format": "csv",
            "input_path": str(input_path),
            "row_count": int(len(frame)),
            "membership_column": membership_column,
            "sample_id_column": sample_id_column,
            "dataset": unique_column_value(frame, "dataset"),
            "model": unique_column_value(frame, "model"),
        },
    )
    validate_common_lengths(scores)
    return scores


def load_scores(config: AuditToolConfig) -> AuditScores:
    input_format = config.input_format.lower()
    if input_format == "npz":
        return load_npz_scores(config.input_path, config.score_names)
    if input_format == "csv":
        return load_csv_scores(
            config.input_path,
            config.score_names,
            membership_column=config.membership_column,
            sample_id_column=config.sample_id_column,
        )
    raise ValueError(f"Unsupported input_format: {config.input_format}")


def metric_functions(fpr_levels: tuple[float, ...]) -> list[tuple[str, Any]]:
    functions: list[tuple[str, Any]] = [("AUC", attack_auc)]
    for fpr in fpr_levels:
        functions.append((metric_label_for_fpr("TPR", fpr), lambda m, n, fpr=fpr: tpr_at_fpr(m, n, fpr)))
        functions.append(
            (
                metric_label_for_fpr("membership_advantage", fpr),
                lambda m, n, fpr=fpr: membership_advantage_at_fpr(m, n, fpr),
            )
        )
    return functions


def point_metric_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    fpr_levels: tuple[float, ...],
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

    for fpr in fpr_levels:
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


def bootstrap_interval_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    fpr_levels: tuple[float, ...],
    n_bootstrap: int,
    confidence: float,
    random_state: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset, (metric_name, metric_fn) in enumerate(metric_functions(fpr_levels)):
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


def fixed_threshold_interval_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    fpr_levels: tuple[float, ...],
    confidence: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fpr in fpr_levels:
        interval = fixed_threshold_tpr_wilson_interval(
            member_scores,
            nonmember_scores,
            fpr,
            confidence=confidence,
        )
        common = {
            "dataset": dataset,
            "model": model,
            "attack_score": score_name,
            "target_fpr": interval["target_fpr"],
            "threshold": interval["threshold"],
            "empirical_fpr": interval["empirical_fpr"],
            "tie_fraction": interval["tie_fraction"],
            "confidence": confidence,
            "method": "fixed_threshold_wilson",
            "member_successes_effective": interval["member_successes_effective"],
            "n_members": int(interval["n_members"]),
            "nonmember_false_positives_effective": interval["nonmember_false_positives_effective"],
            "n_nonmembers": int(interval["n_nonmembers"]),
        }
        rows.append(
            {
                **common,
                "metric": metric_label_for_fpr("TPR", fpr),
                "point": interval["point"],
                "ci_lower": interval["ci_lower"],
                "ci_upper": interval["ci_upper"],
                "ci_width": interval["ci_width"],
            }
        )
        rows.append(
            {
                **common,
                "metric": metric_label_for_fpr("membership_advantage", fpr),
                "point": interval["point"] - interval["empirical_fpr"],
                "ci_lower": interval["ci_lower"] - interval["empirical_fpr"],
                "ci_upper": interval["ci_upper"] - interval["empirical_fpr"],
                "ci_width": interval["ci_width"],
            }
        )
    return rows


def sample_metric_rows(
    *,
    dataset: str,
    model: str,
    score_name: str,
    sample_size: int,
    repeat: int,
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    fpr_levels: tuple[float, ...],
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

    for fpr in fpr_levels:
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


def instability_note(metric: str, sample_size: int, fpr_levels: tuple[float, ...]) -> str:
    for fpr in fpr_levels:
        if metric in {metric_label_for_fpr("TPR", fpr), metric_label_for_fpr("membership_advantage", fpr)}:
            budget = sample_size * fpr
            if budget < 1:
                return "severe_tail_resolution_warning: expected false positives < 1"
            if budget < 5:
                return "tail_resolution_warning: expected false positives < 5"
    return ""


def aggregate_subsampling_rows(
    repeat_rows: list[dict[str, Any]],
    *,
    fpr_levels: tuple[float, ...],
) -> list[dict[str, Any]]:
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
                "instability_note": instability_note(metric, sample_size, fpr_levels),
            }
        )
    return aggregate


def run_array_subsampling(
    *,
    dataset: str,
    model: str,
    scores: AuditScores,
    sample_sizes: tuple[int, ...],
    n_repeats: int,
    random_state: int,
    fpr_levels: tuple[float, ...],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = np.random.default_rng(random_state)
    repeat_rows: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    first_score = scores.score_names[0]
    member_pool_size = len(scores.member_scores[first_score])
    nonmember_pool_size = len(scores.nonmember_scores[first_score])
    max_size = min(member_pool_size, nonmember_pool_size)

    for sample_size in sample_sizes:
        if sample_size > max_size:
            for score_name in scores.score_names:
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
            for score_name in scores.score_names:
                repeat_rows.extend(
                    sample_metric_rows(
                        dataset=dataset,
                        model=model,
                        score_name=score_name,
                        sample_size=sample_size,
                        repeat=repeat,
                        member_scores=scores.member_scores[score_name][member_idx],
                        nonmember_scores=scores.nonmember_scores[score_name][nonmember_idx],
                        fpr_levels=fpr_levels,
                    )
                )

    return repeat_rows, aggregate_subsampling_rows(repeat_rows, fpr_levels=fpr_levels), skipped


def tail_warning_level(expected_false_positives: float) -> str:
    if expected_false_positives < 1:
        return "severe_tail_resolution_warning"
    if expected_false_positives < 5:
        return "tail_resolution_warning"
    return ""


def tail_resolution_warning_rows(
    *,
    dataset: str,
    model: str,
    score_names: tuple[str, ...],
    full_n_nonmembers: int,
    sample_sizes: tuple[int, ...],
    fpr_levels: tuple[float, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    contexts = [("full_input", full_n_nonmembers)] + [(f"sample_size_{size}", size) for size in sample_sizes]
    for score_name in score_names:
        for context, n_nonmembers in contexts:
            for fpr in fpr_levels:
                expected = n_nonmembers * fpr
                rows.append(
                    {
                        "dataset": dataset,
                        "model": model,
                        "attack_score": score_name,
                        "context": context,
                        "n_nonmembers": int(n_nonmembers),
                        "target_fpr": fpr,
                        "expected_false_positives": expected,
                        "warning": tail_warning_level(expected),
                    }
                )
    return rows


def make_low_fpr_roc_figure(figures_dir: Path, scores: AuditScores, fpr_levels: tuple[float, ...]) -> str:
    max_fpr = max(0.05, max(fpr_levels) * 5.0)
    plt.figure(figsize=(7, 5))
    for score_name in scores.score_names:
        y_true = np.concatenate(
            [
                np.ones(len(scores.member_scores[score_name]), dtype=int),
                np.zeros(len(scores.nonmember_scores[score_name]), dtype=int),
            ]
        )
        values = np.concatenate([scores.member_scores[score_name], scores.nonmember_scores[score_name]])
        fpr, tpr, _thresholds = roc_curve(y_true, values)
        mask = fpr <= max_fpr
        plt.plot(fpr[mask], tpr[mask], label=score_name)
    for fpr in fpr_levels:
        plt.axvline(fpr, color="black", linewidth=0.8, linestyle="--", alpha=0.35)
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title("Low-FPR ROC")
    plt.xlim(0, max_fpr)
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    path = figures_dir / "low_fpr_roc.png"
    plt.savefig(path, dpi=200)
    plt.close()
    return str(path)


def make_distribution_figures(figures_dir: Path, scores: AuditScores) -> list[str]:
    paths: list[str] = []
    for score_name in scores.score_names:
        plt.figure(figsize=(7, 5))
        plt.hist(scores.nonmember_scores[score_name], bins=50, alpha=0.6, density=True, label="non-member")
        plt.hist(scores.member_scores[score_name], bins=50, alpha=0.6, density=True, label="member")
        plt.xlabel(score_name)
        plt.ylabel("Density")
        plt.title(f"Member and Non-Member Score Distribution: {score_name}")
        plt.legend()
        plt.tight_layout()
        path = figures_dir / f"score_distribution_{score_name}.png"
        plt.savefig(path, dpi=200)
        plt.close()
        paths.append(str(path))
    return paths


def make_subsampling_figures(figures_dir: Path, aggregate_rows: list[dict[str, Any]]) -> list[str]:
    if not aggregate_rows:
        return []

    paths: list[str] = []
    tpr_rows = [row for row in aggregate_rows if str(row["metric"]).startswith("TPR@")]
    if tpr_rows:
        plt.figure(figsize=(8, 5))
        for key in sorted({(row["attack_score"], row["metric"]) for row in tpr_rows}):
            score_name, metric = key
            series = sorted(
                [row for row in tpr_rows if row["attack_score"] == score_name and row["metric"] == metric],
                key=lambda row: int(row["sample_size"]),
            )
            plt.plot(
                [int(row["sample_size"]) for row in series],
                [float(row["mean"]) for row in series],
                marker="o",
                label=f"{score_name} {metric}",
            )
        plt.xlabel("Balanced audit sample size per group")
        plt.ylabel("Mean TPR")
        plt.title("Low-FPR TPR by Audit Sample Size")
        plt.legend(fontsize=7)
        plt.tight_layout()
        path = figures_dir / "tpr_at_fpr_vs_audit_size.png"
        plt.savefig(path, dpi=200)
        plt.close()
        paths.append(str(path))

    width_rows = [row for row in aggregate_rows if row["metric"] == "AUC" or str(row["metric"]).startswith("TPR@")]
    if width_rows:
        plt.figure(figsize=(8, 5))
        for key in sorted({(row["attack_score"], row["metric"]) for row in width_rows}):
            score_name, metric = key
            series = sorted(
                [row for row in width_rows if row["attack_score"] == score_name and row["metric"] == metric],
                key=lambda row: int(row["sample_size"]),
            )
            plt.plot(
                [int(row["sample_size"]) for row in series],
                [float(row["interval_width"]) for row in series],
                marker="o",
                label=f"{score_name} {metric}",
            )
        plt.xlabel("Balanced audit sample size per group")
        plt.ylabel("Empirical 95% interval width")
        plt.title("Metric Instability by Audit Sample Size")
        plt.legend(fontsize=7)
        plt.tight_layout()
        path = figures_dir / "interval_width_vs_audit_size.png"
        plt.savefig(path, dpi=200)
        plt.close()
        paths.append(str(path))

    return paths


def generate_figures(
    *,
    figures_dir: Path,
    scores: AuditScores,
    fpr_levels: tuple[float, ...],
    subsampling_aggregate: list[dict[str, Any]],
) -> list[str]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = [make_low_fpr_roc_figure(figures_dir, scores, fpr_levels)]
    paths.extend(make_distribution_figures(figures_dir, scores))
    paths.extend(make_subsampling_figures(figures_dir, subsampling_aggregate))
    return paths


def config_payload(
    *,
    config: AuditToolConfig,
    dataset: str,
    model: str,
    scores: AuditScores,
    generated_at: str,
    output_paths: dict[str, str],
    figures: list[str],
) -> dict[str, Any]:
    first_score = scores.score_names[0]
    return {
        "generated_at": generated_at,
        "input_path": str(config.input_path),
        "input_format": config.input_format,
        "output_dir": str(config.output_dir),
        "dataset": dataset,
        "model": model,
        "score_names": list(scores.score_names),
        "n_members": int(len(scores.member_scores[first_score])),
        "n_nonmembers": int(len(scores.nonmember_scores[first_score])),
        "fpr_levels": list(config.fpr_levels),
        "n_bootstrap": config.n_bootstrap,
        "confidence": config.confidence,
        "n_repeats": config.n_repeats,
        "sample_sizes": list(config.sample_sizes),
        "random_state": config.random_state,
        "membership_column": config.membership_column,
        "sample_id_column": config.sample_id_column,
        "make_figures": config.make_figures,
        "input_metadata": scores.metadata,
        "outputs": output_paths,
        "figures": figures,
    }


def run_summary_text(payload: dict[str, Any], main_rows: list[dict[str, Any]], warning_rows: list[dict[str, Any]]) -> str:
    auc_rows = [row for row in main_rows if row["metric"] == "AUC"]
    auc_rows = sorted(auc_rows, key=lambda row: row["value"], reverse=True)
    active_warnings = [row for row in warning_rows if row["warning"]]

    lines = [
        "# Reusable Audit Tool Run Summary",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Input",
        "",
        f"- Input path: `{payload['input_path']}`",
        f"- Input format: `{payload['input_format']}`",
        f"- Dataset label: `{payload['dataset']}`",
        f"- Model label: `{payload['model']}`",
        f"- Score names: `{payload['score_names']}`",
        f"- Members / non-members: {payload['n_members']} / {payload['n_nonmembers']}",
        "",
        "## Settings",
        "",
        f"- FPR levels: `{payload['fpr_levels']}`",
        f"- Bootstrap repeats: {payload['n_bootstrap']}",
        f"- Confidence: {payload['confidence']}",
        f"- Subsampling repeats: {payload['n_repeats']}",
        f"- Sample sizes: `{payload['sample_sizes']}`",
        f"- Random state: {payload['random_state']}",
        "",
        "## Outputs",
        "",
    ]
    for label, path in payload["outputs"].items():
        lines.append(f"- {label}: `{path}`")

    lines.extend(
        [
            "",
            "## AUC Snapshot",
            "",
            "| Attack Score | AUC |",
            "| --- | ---: |",
        ]
    )
    for row in auc_rows:
        lines.append(f"| {row['attack_score']} | {row['value']:.4f} |")

    lines.extend(
        [
            "",
            "## Tail-Resolution Warnings",
            "",
        ]
    )
    if active_warnings:
        lines.extend(
            [
                "| Attack Score | Context | Target FPR | Expected FPs | Warning |",
                "| --- | --- | ---: | ---: | --- |",
            ]
        )
        for row in active_warnings[:40]:
            lines.append(
                f"| {row['attack_score']} | {row['context']} | {row['target_fpr']} | "
                f"{row['expected_false_positives']:.3f} | {row['warning']} |"
            )
    else:
        lines.append("- No automatic low-FPR tail-resolution warnings.")

    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- Larger scores are interpreted as more member-like.",
            "- Low-FPR metrics use tie-aware randomized threshold handling.",
            "- Bootstrap intervals resample member and non-member scores separately.",
            "- Fixed-threshold Wilson intervals are conditional on the selected threshold/tie rule.",
            "- Subsampling rows estimate how metrics vary when the balanced audit sample is smaller than the available score pool.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_audit(config: AuditToolConfig) -> dict[str, Any]:
    scores = load_scores(config)
    output_dir = config.output_dir
    metrics_dir = output_dir / "metrics"
    subsampling_dir = output_dir / "subsampling"
    diagnostics_dir = output_dir / "diagnostics"
    figures_dir = output_dir / "figures"
    for path in (metrics_dir, subsampling_dir, diagnostics_dir):
        path.mkdir(parents=True, exist_ok=True)

    dataset = config.dataset or str(scores.metadata.get("dataset") or config.input_path.stem)
    model = config.model or str(scores.metadata.get("model") or "score_arrays")

    main_rows: list[dict[str, Any]] = []
    ci_rows: list[dict[str, Any]] = []
    fixed_rows: list[dict[str, Any]] = []
    for score_index, score_name in enumerate(scores.score_names):
        member_scores = scores.member_scores[score_name]
        nonmember_scores = scores.nonmember_scores[score_name]
        main_rows.extend(
            point_metric_rows(
                dataset=dataset,
                model=model,
                score_name=score_name,
                member_scores=member_scores,
                nonmember_scores=nonmember_scores,
                fpr_levels=config.fpr_levels,
            )
        )
        ci_rows.extend(
            bootstrap_interval_rows(
                dataset=dataset,
                model=model,
                score_name=score_name,
                member_scores=member_scores,
                nonmember_scores=nonmember_scores,
                fpr_levels=config.fpr_levels,
                n_bootstrap=config.n_bootstrap,
                confidence=config.confidence,
                random_state=config.random_state + score_index * 1000,
            )
        )
        fixed_rows.extend(
            fixed_threshold_interval_rows(
                dataset=dataset,
                model=model,
                score_name=score_name,
                member_scores=member_scores,
                nonmember_scores=nonmember_scores,
                fpr_levels=config.fpr_levels,
                confidence=config.confidence,
            )
        )

    repeat_rows, aggregate_rows, skipped_rows = run_array_subsampling(
        dataset=dataset,
        model=model,
        scores=scores,
        sample_sizes=config.sample_sizes,
        n_repeats=config.n_repeats,
        random_state=config.random_state,
        fpr_levels=config.fpr_levels,
    )

    first_score = scores.score_names[0]
    warning_rows = tail_resolution_warning_rows(
        dataset=dataset,
        model=model,
        score_names=scores.score_names,
        full_n_nonmembers=len(scores.nonmember_scores[first_score]),
        sample_sizes=config.sample_sizes,
        fpr_levels=config.fpr_levels,
    )

    main_path = metrics_dir / "main_metrics.csv"
    ci_path = metrics_dir / "confidence_intervals.csv"
    fixed_path = metrics_dir / "fixed_threshold_intervals.csv"
    repeat_path = subsampling_dir / "sample_size_repeats.csv"
    aggregate_path = subsampling_dir / "sample_size_sensitivity.csv"
    skipped_path = subsampling_dir / "sample_size_skipped.csv"
    warning_path = diagnostics_dir / "tail_resolution_warnings.csv"
    run_config_path = output_dir / "run_config.json"
    summary_path = output_dir / "run_summary.md"

    write_csv(main_path, main_rows)
    write_csv(ci_path, ci_rows)
    write_csv(fixed_path, fixed_rows)
    write_csv(repeat_path, repeat_rows, fieldnames=[
        "dataset",
        "model",
        "attack_score",
        "sample_size",
        "repeat",
        "metric",
        "value",
        "fp_budget",
    ])
    write_csv(aggregate_path, aggregate_rows, fieldnames=[
        "dataset",
        "model",
        "attack_score",
        "sample_size",
        "metric",
        "n_repeats",
        "mean",
        "std",
        "p025",
        "median",
        "p975",
        "interval_width",
        "min",
        "max",
        "instability_note",
    ])
    write_csv(skipped_path, skipped_rows, fieldnames=["dataset", "model", "attack_score", "sample_size", "reason"])
    write_csv(warning_path, warning_rows)

    figure_paths: list[str] = []
    if config.make_figures:
        figure_paths = generate_figures(
            figures_dir=figures_dir,
            scores=scores,
            fpr_levels=config.fpr_levels,
            subsampling_aggregate=aggregate_rows,
        )

    output_paths = {
        "main_metrics": str(main_path),
        "confidence_intervals": str(ci_path),
        "fixed_threshold_intervals": str(fixed_path),
        "sample_size_repeats": str(repeat_path),
        "sample_size_sensitivity": str(aggregate_path),
        "sample_size_skipped": str(skipped_path),
        "tail_resolution_warnings": str(warning_path),
        "run_config": str(run_config_path),
        "run_summary": str(summary_path),
    }
    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    payload = config_payload(
        config=config,
        dataset=dataset,
        model=model,
        scores=scores,
        generated_at=generated_at,
        output_paths=output_paths,
        figures=figure_paths,
    )
    write_json(run_config_path, payload)
    summary_path.write_text(run_summary_text(payload, main_rows, warning_rows), encoding="utf-8")
    return payload
