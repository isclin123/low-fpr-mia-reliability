from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATASETS = (
    "credit_default",
    "covertype",
    "adult_income",
    "bank_marketing",
    "diabetes_readmission",
)
SCORES = ("neg_loss", "confidence", "neg_entropy", "modified_entropy")
METRICS = ("AUC", "TPR@1%FPR", "TPR@0.1%FPR")
ID_LIKE_TOKENS = ("id", "_id", "encounter", "patient_nbr", "duration")


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def row_view(array: np.ndarray) -> np.ndarray:
    contiguous = np.ascontiguousarray(array)
    dtype = np.dtype((np.void, contiguous.dtype.itemsize * contiguous.shape[1]))
    return contiguous.view(dtype).reshape(contiguous.shape[0])


def count_unique_rows(values: np.ndarray) -> int:
    return int(np.unique(values).size)


def duplicate_checks(project_root: Path, dataset: str) -> dict[str, Any]:
    cleaned_dir = project_root / "data_processed" / dataset
    data = np.load(cleaned_dir / "cleaned_dataset.npz")
    split = np.load(cleaned_dir / "member_nonmember_split.npz")
    metadata = read_json(cleaned_dir / "metadata.json")

    X = data["X"]
    member_idx = split["member_idx"]
    nonmember_idx = split["nonmember_idx"]
    member_set = set(member_idx.tolist())
    nonmember_set = set(nonmember_idx.tolist())

    views = row_view(X)
    member_rows = views[member_idx]
    nonmember_rows = views[nonmember_idx]
    member_unique_values = np.unique(member_rows)
    nonmember_unique_values = np.unique(nonmember_rows)
    member_unique = int(member_unique_values.size)
    nonmember_unique = int(nonmember_unique_values.size)
    all_unique = count_unique_rows(views)

    cross_unique_overlap = int(np.intersect1d(member_unique_values, nonmember_unique_values).size)
    member_rows_seen_in_nonmember = int(np.isin(member_rows, nonmember_unique_values).sum())
    nonmember_rows_seen_in_member = int(np.isin(nonmember_rows, member_unique_values).sum())

    feature_names = [str(item) for item in metadata.get("feature_names", [])]
    flagged_features = [
        name
        for name in feature_names
        if name.lower() == "id"
        or name.lower().endswith("_id")
        or any(token in name.lower() for token in ID_LIKE_TOKENS[2:])
    ]

    return {
        "dataset": dataset,
        "n_rows": int(X.shape[0]),
        "n_features": int(X.shape[1]),
        "member_rows": int(member_idx.size),
        "nonmember_rows": int(nonmember_idx.size),
        "member_nonmember_index_overlap": int(len(member_set & nonmember_set)),
        "all_unique_feature_rows": all_unique,
        "all_duplicate_row_fraction": float(1.0 - all_unique / X.shape[0]),
        "member_unique_feature_rows": member_unique,
        "member_duplicate_row_fraction": float(1.0 - member_unique / member_idx.size),
        "nonmember_unique_feature_rows": nonmember_unique,
        "nonmember_duplicate_row_fraction": float(1.0 - nonmember_unique / nonmember_idx.size),
        "cross_split_unique_feature_overlap": int(cross_unique_overlap),
        "member_rows_with_feature_duplicate_in_nonmember": member_rows_seen_in_nonmember,
        "nonmember_rows_with_feature_duplicate_in_member": nonmember_rows_seen_in_member,
        "id_like_feature_count": len(flagged_features),
        "id_like_features": ";".join(flagged_features),
    }


def largest_tie_fraction(values: np.ndarray) -> float:
    if values.size == 0:
        return float("nan")
    _, counts = np.unique(values, return_counts=True)
    return float(counts.max() / values.size)


def score_diagnostics(
    metrics: pd.DataFrame,
    results_root: Path,
    dataset: str,
) -> list[dict[str, Any]]:
    score_path = results_root / "attack_scores" / dataset / "extra_trees" / "attack_scores.npz"
    arrays = np.load(score_path)
    rows: list[dict[str, Any]] = []

    metric_subset = metrics[(metrics["dataset"] == dataset) & (metrics["model"] == "extra_trees")]

    for score in SCORES:
        member = arrays[f"member_{score}"]
        nonmember = arrays[f"nonmember_{score}"]
        combined = np.concatenate([member, nonmember])
        finite_member = np.isfinite(member)
        finite_nonmember = np.isfinite(nonmember)
        max_member = np.nanmax(member)

        metric_values = {
            row["metric"]: float(row["value"])
            for _, row in metric_subset[metric_subset["attack_score"] == score].iterrows()
            if row["metric"] in METRICS
        }

        rows.append(
            {
                "dataset": dataset,
                "score": score,
                "auc": metric_values.get("AUC", float("nan")),
                "tpr_at_1pct_fpr": metric_values.get("TPR@1%FPR", float("nan")),
                "tpr_at_0_1pct_fpr": metric_values.get("TPR@0.1%FPR", float("nan")),
                "n_member": int(member.size),
                "n_nonmember": int(nonmember.size),
                "member_nonfinite": int((~finite_member).sum()),
                "nonmember_nonfinite": int((~finite_nonmember).sum()),
                "combined_nonfinite": int((~np.isfinite(combined)).sum()),
                "member_mean": float(np.nanmean(member)),
                "nonmember_mean": float(np.nanmean(nonmember)),
                "mean_gap_member_minus_nonmember": float(np.nanmean(member) - np.nanmean(nonmember)),
                "member_std": float(np.nanstd(member)),
                "nonmember_std": float(np.nanstd(nonmember)),
                "member_min": float(np.nanmin(member)),
                "member_median": float(np.nanmedian(member)),
                "member_max": float(max_member),
                "nonmember_min": float(np.nanmin(nonmember)),
                "nonmember_median": float(np.nanmedian(nonmember)),
                "nonmember_max": float(np.nanmax(nonmember)),
                "member_unique_values": int(np.unique(member).size),
                "nonmember_unique_values": int(np.unique(nonmember).size),
                "member_largest_tie_fraction": largest_tie_fraction(member),
                "nonmember_largest_tie_fraction": largest_tie_fraction(nonmember),
                "member_at_member_max_fraction": float(np.mean(member == max_member)),
                "nonmember_at_member_max_fraction": float(np.mean(nonmember == max_member)),
            }
        )
    return rows


def model_gap_summary(project_root: Path, results_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        model_metadata = read_json(results_root / "models" / dataset / "extra_trees" / "metadata.json")
        dataset_metadata = read_json(project_root / "data_processed" / dataset / "metadata.json")
        rows.append(
            {
                "dataset": dataset,
                "train_accuracy": float(model_metadata["train_accuracy"]),
                "nonmember_accuracy": float(model_metadata["nonmember_accuracy"]),
                "accuracy_gap_train_minus_nonmember": float(
                    model_metadata["train_accuracy"] - model_metadata["nonmember_accuracy"]
                ),
                "train_log_loss": float(model_metadata["train_log_loss"]),
                "nonmember_log_loss": float(model_metadata["nonmember_log_loss"]),
                "log_loss_gap_nonmember_minus_train": float(
                    model_metadata["nonmember_log_loss"] - model_metadata["train_log_loss"]
                ),
                "train_size": int(model_metadata["train_size"]),
                "nonmember_pool_size": int(model_metadata["nonmember_pool_size"]),
                "n_rows": int(model_metadata["n_rows"]),
                "n_features": int(model_metadata["n_features"]),
                "labels": ";".join(str(item) for item in model_metadata["labels"]),
                "max_train_samples": model_metadata["max_train_samples"],
                "model_config": json.dumps(model_metadata["model_config"], sort_keys=True),
                "target_name": dataset_metadata["target_name"],
                "task_type": dataset_metadata["task_type"],
            }
        )
    return rows


def metric_snapshot(metrics: pd.DataFrame) -> pd.DataFrame:
    subset = metrics[(metrics["model"] == "extra_trees") & (metrics["metric"].isin(METRICS))]
    pivot = subset.pivot_table(
        index=["dataset", "attack_score"],
        columns="metric",
        values="value",
        aggfunc="first",
    ).reset_index()
    pivot.columns.name = None
    pivot = pivot.rename(
        columns={
            "AUC": "auc",
            "TPR@1%FPR": "tpr_at_1pct_fpr",
            "TPR@0.1%FPR": "tpr_at_0_1pct_fpr",
        }
    )
    return pivot.sort_values(["dataset", "auc"], ascending=[True, False])


def write_summary(
    out_dir: Path,
    model_df: pd.DataFrame,
    score_df: pd.DataFrame,
    duplicate_df: pd.DataFrame,
    metric_df: pd.DataFrame,
) -> None:
    generated = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    best_auc = (
        metric_df.sort_values(["dataset", "auc"], ascending=[True, False])
        .groupby("dataset", as_index=False)
        .first()[["dataset", "attack_score", "auc", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"]]
    )
    scores_above_09 = score_df.groupby("dataset")["auc"].apply(lambda s: int((s >= 0.9).sum())).reset_index()
    scores_above_09 = scores_above_09.rename(columns={"auc": "scores_with_auc_ge_0_9"})

    lines = [
        "# ExtraTrees Sanity-Check Generated Summary",
        "",
        f"Generated: {generated}",
        "",
        "## Best ExtraTrees Score per Dataset",
        "",
        best_auc.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Train versus Nonmember Gap",
        "",
        model_df[
            [
                "dataset",
                "train_accuracy",
                "nonmember_accuracy",
                "accuracy_gap_train_minus_nonmember",
                "train_log_loss",
                "nonmember_log_loss",
                "log_loss_gap_nonmember_minus_train",
            ]
        ].to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Cross-Score Consistency",
        "",
        scores_above_09.to_markdown(index=False),
        "",
        "## Duplicate / Split Checks",
        "",
        duplicate_df[
            [
                "dataset",
                "member_nonmember_index_overlap",
                "all_duplicate_row_fraction",
                "cross_split_unique_feature_overlap",
                "member_rows_with_feature_duplicate_in_nonmember",
                "nonmember_rows_with_feature_duplicate_in_member",
                "id_like_feature_count",
                "id_like_features",
            ]
        ].to_markdown(index=False, floatfmt=".6f"),
        "",
    ]
    (out_dir / "generated_summary.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ExtraTrees sanity checks from existing stage1 outputs.")
    parser.add_argument("--project-root", type=Path, default=default_project_root())
    parser.add_argument("--results-subdir", default="expanded_tabular_stage1")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    results_root = project_root / "analysis" / "results" / args.results_subdir
    out_dir = args.output_dir or project_root / "analysis" / "results" / "extratrees_sanity_check"
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = pd.read_csv(results_root / "metrics" / "main_metrics.csv")
    model_df = pd.DataFrame(model_gap_summary(project_root, results_root))
    score_df = pd.DataFrame(
        row
        for dataset in DATASETS
        for row in score_diagnostics(metrics, results_root, dataset)
    )
    duplicate_df = pd.DataFrame(duplicate_checks(project_root, dataset) for dataset in DATASETS)
    metric_df = metric_snapshot(metrics)

    model_df.to_csv(out_dir / "model_gap_summary.csv", index=False)
    score_df.to_csv(out_dir / "score_diagnostics.csv", index=False)
    duplicate_df.to_csv(out_dir / "split_duplicate_checks.csv", index=False)
    metric_df.to_csv(out_dir / "metric_snapshot.csv", index=False)
    write_summary(out_dir, model_df, score_df, duplicate_df, metric_df)

    print(f"Wrote ExtraTrees sanity-check outputs to {out_dir}")


if __name__ == "__main__":
    main()
