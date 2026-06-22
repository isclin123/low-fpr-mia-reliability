from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 8,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.8,
        "legend.frameon": False,
    }
)

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_NAME = "expanded_tabular_stage1"
RESULTS_DIR = PROJECT_ROOT / "05_analysis" / "results" / RUN_NAME
OUTPUT_DIR = PROJECT_ROOT / "06_figures_tables" / "expanded"

DATASET_ORDER = [
    "credit_default",
    "covertype",
    "adult_income",
    "bank_marketing",
    "diabetes_readmission",
]
DATASET_LABELS = {
    "credit_default": "Credit Default",
    "covertype": "Covertype",
    "adult_income": "Adult Income",
    "bank_marketing": "Bank Marketing",
    "diabetes_readmission": "Diabetes Readmission",
}
MODEL_ORDER = [
    "logistic_regression",
    "hist_gradient_boosting",
    "random_forest",
    "extra_trees",
    "small_mlp",
]
MODEL_LABELS = {
    "logistic_regression": "Logistic",
    "hist_gradient_boosting": "HistGB",
    "random_forest": "Random Forest",
    "extra_trees": "ExtraTrees",
    "small_mlp": "Small MLP",
}
SCORE_LABELS = {
    "neg_loss": "Negative loss",
    "confidence": "Confidence",
    "neg_entropy": "Negative entropy",
    "modified_entropy": "Modified entropy",
}
MODEL_COLORS = {
    "logistic_regression": "#4C78A8",
    "hist_gradient_boosting": "#59A14F",
    "random_forest": "#E15759",
    "extra_trees": "#B07AA1",
    "small_mlp": "#F28E2B",
}
SAMPLE_SIZES = [250, 500, 1000, 2000, 5000]
FPR_LEVELS = [0.01, 0.001]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.gcf()
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(path, dpi=400, bbox_inches="tight")
    plt.close(fig)


def load_main_metrics() -> pd.DataFrame:
    metrics = pd.read_csv(RESULTS_DIR / "metrics" / "main_metrics.csv")
    metrics["dataset"] = pd.Categorical(metrics["dataset"], DATASET_ORDER, ordered=True)
    metrics["model"] = pd.Categorical(metrics["model"], MODEL_ORDER, ordered=True)
    return metrics.sort_values(["dataset", "model", "attack_score", "metric"]).reset_index(drop=True)


def load_subsampling() -> pd.DataFrame:
    sensitivity = pd.read_csv(RESULTS_DIR / "subsampling" / "sample_size_sensitivity.csv")
    sensitivity["dataset"] = pd.Categorical(sensitivity["dataset"], DATASET_ORDER, ordered=True)
    sensitivity["model"] = pd.Categorical(sensitivity["model"], MODEL_ORDER, ordered=True)
    return sensitivity.sort_values(["dataset", "model", "attack_score", "sample_size", "metric"]).reset_index(drop=True)


def load_model_metadata() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted((RESULTS_DIR / "models").glob("*/*/metadata.json")):
        data = read_json(path)
        rows.append(
            {
                "dataset": data["dataset"],
                "model": data["model"],
                "train_accuracy": data["train_accuracy"],
                "nonmember_accuracy": data["nonmember_accuracy"],
                "accuracy_gap": data["train_accuracy"] - data["nonmember_accuracy"],
                "train_log_loss": data["train_log_loss"],
                "nonmember_log_loss": data["nonmember_log_loss"],
                "log_loss_gap": data["nonmember_log_loss"] - data["train_log_loss"],
                "n_members": data["member_pool_size"],
                "n_nonmembers": data["nonmember_pool_size"],
                "n_features": data["n_features"],
            }
        )
    metadata = pd.DataFrame(rows)
    metadata["dataset"] = pd.Categorical(metadata["dataset"], DATASET_ORDER, ordered=True)
    metadata["model"] = pd.Categorical(metadata["model"], MODEL_ORDER, ordered=True)
    return metadata.sort_values(["dataset", "model"]).reset_index(drop=True)


def build_summary_tables(metrics: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    auc = metrics[metrics["metric"].eq("AUC")].copy()
    best_auc = (
        auc.sort_values("value", ascending=False)
        .groupby(["dataset", "model"], observed=True)
        .head(1)
        .loc[:, ["dataset", "model", "attack_score", "value"]]
        .rename(columns={"attack_score": "best_auc_score", "value": "best_auc"})
    )
    neg_loss_low = metrics[
        metrics["attack_score"].eq("neg_loss") & metrics["metric"].isin(["TPR@1%FPR", "TPR@0.1%FPR"])
    ].pivot_table(index=["dataset", "model"], columns="metric", values="value", observed=True).reset_index()

    summary = metadata.merge(best_auc, on=["dataset", "model"], how="left").merge(
        neg_loss_low,
        on=["dataset", "model"],
        how="left",
    )
    summary = summary.rename(
        columns={
            "TPR@1%FPR": "neg_loss_tpr_at_1pct_fpr",
            "TPR@0.1%FPR": "neg_loss_tpr_at_0_1pct_fpr",
        }
    )
    summary = summary[
        [
            "dataset",
            "model",
            "n_members",
            "n_nonmembers",
            "n_features",
            "train_accuracy",
            "nonmember_accuracy",
            "accuracy_gap",
            "best_auc",
            "best_auc_score",
            "neg_loss_tpr_at_1pct_fpr",
            "neg_loss_tpr_at_0_1pct_fpr",
        ]
    ].sort_values(["dataset", "model"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_DIR / "expanded_model_comparison_summary.csv", index=False)

    markdown = summary.copy()
    markdown["dataset"] = markdown["dataset"].astype(str).map(DATASET_LABELS)
    markdown["model"] = markdown["model"].astype(str).map(MODEL_LABELS)
    markdown["best_auc_score"] = markdown["best_auc_score"].map(SCORE_LABELS)
    for column in [
        "train_accuracy",
        "nonmember_accuracy",
        "accuracy_gap",
        "best_auc",
        "neg_loss_tpr_at_1pct_fpr",
        "neg_loss_tpr_at_0_1pct_fpr",
    ]:
        markdown[column] = markdown[column].map(lambda value: f"{value:.4f}")
    md_text = "# Expanded Model Comparison Summary\n\n"
    md_text += "Run: `expanded_tabular_stage1`\n\n"
    md_text += markdown.to_markdown(index=False)
    md_text += "\n"
    (OUTPUT_DIR / "expanded_model_comparison_summary.md").write_text(md_text, encoding="utf-8")
    return summary


def plot_best_auc_heatmap(summary: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "expanded_best_auc_heatmap.png"
    heat = summary.pivot(index="dataset", columns="model", values="best_auc")
    heat.index = [DATASET_LABELS[str(value)] for value in heat.index]
    heat.columns = [MODEL_LABELS[str(value)] for value in heat.columns]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.heatmap(
        heat,
        vmin=0.5,
        vmax=1.0,
        annot=True,
        fmt=".3f",
        cmap="viridis",
        linewidths=0.5,
        cbar_kws={"label": "AUC"},
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title("Best MIA AUC across target models")
    savefig(path)
    return path


def plot_low_fpr_heatmaps(summary: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "expanded_neg_loss_low_fpr_heatmaps.png"
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 5.8))
    for ax, column, title, vmax in [
        (axes[0], "neg_loss_tpr_at_1pct_fpr", "Negative-loss TPR at 1% FPR", 1.0),
        (axes[1], "neg_loss_tpr_at_0_1pct_fpr", "Negative-loss TPR at 0.1% FPR", 0.4),
    ]:
        heat = summary.pivot(index="dataset", columns="model", values=column)
        heat.index = [DATASET_LABELS[str(value)] for value in heat.index]
        heat.columns = [MODEL_LABELS[str(value)] for value in heat.columns]
        sns.heatmap(
            heat,
            vmin=0.0,
            vmax=vmax,
            annot=True,
            fmt=".3f",
            cmap="mako",
            linewidths=0.5,
            cbar_kws={"label": "TPR"},
            ax=ax,
        )
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title(title)
    fig.subplots_adjust(wspace=0.36)
    savefig(path)
    return path


def plot_gap_vs_auc(summary: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "expanded_accuracy_gap_vs_best_auc.png"
    plot_data = summary.copy()
    plot_data["dataset_label"] = plot_data["dataset"].astype(str).map(DATASET_LABELS)
    plot_data["model_label"] = plot_data["model"].astype(str).map(MODEL_LABELS)

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    for model in MODEL_ORDER:
        subset = plot_data[plot_data["model"].astype(str).eq(model)]
        ax.scatter(
            subset["accuracy_gap"],
            subset["best_auc"],
            s=95,
            color=MODEL_COLORS[model],
            edgecolor="white",
            linewidth=1.1,
            label=MODEL_LABELS[model],
        )
    ax.axhline(0.5, color="#333333", linewidth=1.0, linestyle="--")
    ax.set_xlabel("Train minus non-member accuracy")
    ax.set_ylabel("Best attack AUC")
    ax.set_title("Train/non-member accuracy gap and best MIA AUC")
    ax.grid(True, color="#E6E6E6", linewidth=0.6)
    ax.legend(frameon=False, ncol=1, loc="center left", bbox_to_anchor=(1.02, 0.5))
    savefig(path)
    return path


def plot_auc_width_by_sample_size(sensitivity: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "expanded_auc_width_by_audit_size.png"
    auc = sensitivity[sensitivity["metric"].eq("AUC")].copy()
    best_score = (
        auc.sort_values("mean", ascending=False)
        .groupby(["dataset", "model", "sample_size"], observed=True)
        .head(1)
        .copy()
    )
    model_mean = (
        best_score.groupby(["model", "sample_size"], observed=True)["interval_width"]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    for model in MODEL_ORDER:
        subset = model_mean[model_mean["model"].astype(str).eq(model)]
        ax.plot(
            subset["sample_size"],
            subset["interval_width"],
            marker="o",
            color=MODEL_COLORS[model],
            label=MODEL_LABELS[model],
        )
    ax.set_xscale("log")
    ax.set_xticks(SAMPLE_SIZES)
    ax.set_xticklabels([str(value) for value in SAMPLE_SIZES])
    ax.set_xlabel("Balanced audit sample size per group")
    ax.set_ylabel("Mean 95% subsampling interval width")
    ax.set_title("AUC variability decreases with audit sample size")
    ax.grid(True, color="#E6E6E6", linewidth=0.6)
    ax.legend(frameon=False)
    savefig(path)
    return path


def plot_tpr001_width_by_sample_size(sensitivity: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "expanded_tpr001_width_by_audit_size.png"
    tpr = sensitivity[
        sensitivity["attack_score"].eq("neg_loss")
        & sensitivity["metric"].eq("TPR@0.1%FPR")
    ].copy()
    model_mean = (
        tpr.groupby(["model", "sample_size"], observed=True)["interval_width"]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    for model in MODEL_ORDER:
        subset = model_mean[model_mean["model"].astype(str).eq(model)]
        ax.plot(
            subset["sample_size"],
            subset["interval_width"],
            marker="o",
            color=MODEL_COLORS[model],
            label=MODEL_LABELS[model],
        )
    ax.set_xscale("log")
    ax.set_xticks(SAMPLE_SIZES)
    ax.set_xticklabels([str(value) for value in SAMPLE_SIZES])
    ax.set_xlabel("Balanced audit sample size per group")
    ax.set_ylabel("Mean 95% subsampling interval width")
    ax.set_title("TPR@0.1%FPR variability decreases with audit sample size")
    ax.grid(True, color="#E6E6E6", linewidth=0.6)
    ax.legend(frameon=False)
    savefig(path)
    return path


def write_sample_size_requirements(metadata: pd.DataFrame) -> Path:
    path = RESULTS_DIR / "sample_size_requirements.md"
    rows = []
    for n_nonmembers in SAMPLE_SIZES:
        for fpr in FPR_LEVELS:
            rows.append(
                {
                    "n_nonmembers": n_nonmembers,
                    "target_fpr": fpr,
                    "expected_false_positives": n_nonmembers * fpr,
                    "warning": "severe" if n_nonmembers * fpr < 1 else "warning" if n_nonmembers * fpr < 5 else "",
                }
            )
    budget = pd.DataFrame(rows)

    min_rows = []
    for fpr in FPR_LEVELS:
        for expected in [1, 5, 10]:
            min_rows.append(
                {
                    "target_fpr": fpr,
                    "expected_false_positives": expected,
                    "required_nonmembers": int(expected / fpr),
                }
            )
    minimums = pd.DataFrame(min_rows)

    dataset_sizes = (
        metadata[["dataset", "n_members", "n_nonmembers"]]
        .drop_duplicates()
        .sort_values("dataset")
        .copy()
    )
    dataset_sizes["dataset"] = dataset_sizes["dataset"].astype(str).map(DATASET_LABELS)

    text = [
        "# Expanded Stage1 Low-FPR Sample-Size Requirements",
        "",
        "This note records why low-FPR audit claims require large non-member audit pools.",
        "",
        "## Dataset Audit Pools",
        "",
        dataset_sizes.to_markdown(index=False),
        "",
        "## Expected False-Positive Budgets",
        "",
        budget.to_markdown(index=False),
        "",
        "## Minimum Non-Member Counts",
        "",
        minimums.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- At 1% FPR, 500 non-members gives only 5 expected false positives.",
        "- At 0.1% FPR, even 5000 non-members gives only 5 expected false positives.",
        "- Audit sizes below these thresholds can still be reported, but they should carry tail-resolution warnings.",
        "- These constraints are statistical, not implementation bugs.",
    ]
    path.write_text("\n".join(text) + "\n", encoding="utf-8")
    return path


def main() -> None:
    metrics = load_main_metrics()
    sensitivity = load_subsampling()
    metadata = load_model_metadata()
    summary = build_summary_tables(metrics, metadata)

    figure_paths = [
        plot_best_auc_heatmap(summary),
        plot_low_fpr_heatmaps(summary),
        plot_gap_vs_auc(summary),
        plot_auc_width_by_sample_size(sensitivity),
        plot_tpr001_width_by_sample_size(sensitivity),
    ]
    requirement_path = write_sample_size_requirements(metadata)

    print(f"summary={OUTPUT_DIR / 'expanded_model_comparison_summary.csv'}")
    for path in figure_paths:
        print(f"figure={path}")
    print(f"sample_size_requirements={requirement_path}")


if __name__ == "__main__":
    main()
