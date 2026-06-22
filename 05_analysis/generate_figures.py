from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import roc_curve


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = PROJECT_ROOT / "05_analysis" / "results"
FIGURE_ROOT = PROJECT_ROOT / "06_figures_tables"
OUTPUT_DIR = FIGURE_ROOT / "diagnostics"

MODEL_ORDER = ["logistic_regression", "hist_gradient_boosting", "random_forest"]
MODEL_LABELS = {
    "logistic_regression": "Logistic",
    "hist_gradient_boosting": "HistGB",
    "random_forest": "Random Forest",
}
DATASET_ORDER = ["credit_default", "covertype"]
DATASET_LABELS = {
    "credit_default": "Credit Default",
    "covertype": "Covertype",
}
SCORE_ORDER = ["neg_loss", "confidence", "neg_entropy", "modified_entropy"]
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
}
MEMBERSHIP_COLORS = {"Member": "#D95F02", "Non-member": "#1B9E77"}
AUDIT_SIZE_TICKS = [250, 500, 1000, 2000, 5000]


def load_main_metrics() -> pd.DataFrame:
    paths = [
        RESULTS_ROOT / "core" / "metrics" / "main_metrics.csv",
        RESULTS_ROOT / "model_extension_hgb" / "metrics" / "main_metrics.csv",
    ]
    frames = [pd.read_csv(path) for path in paths]
    metrics = pd.concat(frames, ignore_index=True)
    metrics = metrics[metrics["model"].isin(MODEL_ORDER)].copy()
    metrics["model_label"] = metrics["model"].map(MODEL_LABELS)
    metrics["dataset_label"] = metrics["dataset"].map(DATASET_LABELS)
    metrics["score_label"] = metrics["attack_score"].map(SCORE_LABELS)
    metrics["model"] = pd.Categorical(metrics["model"], MODEL_ORDER, ordered=True)
    metrics["dataset"] = pd.Categorical(metrics["dataset"], DATASET_ORDER, ordered=True)
    metrics["attack_score"] = pd.Categorical(metrics["attack_score"], SCORE_ORDER, ordered=True)
    return metrics.sort_values(["dataset", "model", "attack_score", "metric"]).reset_index(drop=True)


def load_subsampling() -> pd.DataFrame:
    paths = [
        RESULTS_ROOT / "core" / "subsampling" / "sample_size_sensitivity.csv",
        RESULTS_ROOT / "model_extension_hgb" / "subsampling" / "sample_size_sensitivity.csv",
    ]
    frames = [pd.read_csv(path) for path in paths]
    sensitivity = pd.concat(frames, ignore_index=True)
    sensitivity = sensitivity[sensitivity["model"].isin(MODEL_ORDER)].copy()
    sensitivity["model_label"] = sensitivity["model"].map(MODEL_LABELS)
    sensitivity["dataset_label"] = sensitivity["dataset"].map(DATASET_LABELS)
    sensitivity["score_label"] = sensitivity["attack_score"].map(SCORE_LABELS)
    sensitivity["model"] = pd.Categorical(sensitivity["model"], MODEL_ORDER, ordered=True)
    sensitivity["dataset"] = pd.Categorical(sensitivity["dataset"], DATASET_ORDER, ordered=True)
    return sensitivity.sort_values(["dataset", "model", "attack_score", "sample_size", "metric"]).reset_index(drop=True)


def load_model_metadata() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    metadata_paths = list((RESULTS_ROOT / "core" / "models").glob("*/*/metadata.json"))
    metadata_paths += list((RESULTS_ROOT / "model_extension_hgb" / "models").glob("*/*/metadata.json"))
    for path in metadata_paths:
        with path.open() as handle:
            data = json.load(handle)
        if data["model"] not in MODEL_ORDER:
            continue
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
            }
        )
    metadata = pd.DataFrame(rows)
    metadata["model_label"] = metadata["model"].map(MODEL_LABELS)
    metadata["dataset_label"] = metadata["dataset"].map(DATASET_LABELS)
    metadata["model"] = pd.Categorical(metadata["model"], MODEL_ORDER, ordered=True)
    metadata["dataset"] = pd.Categorical(metadata["dataset"], DATASET_ORDER, ordered=True)
    return metadata.sort_values(["dataset", "model"]).reset_index(drop=True)


def load_attack_scores(dataset: str, model: str, score: str) -> tuple[np.ndarray, np.ndarray]:
    run_name = "model_extension_hgb" if model == "hist_gradient_boosting" else "core"
    score_path = RESULTS_ROOT / run_name / "attack_scores" / dataset / model / "attack_scores.npz"
    with np.load(score_path) as scores:
        return scores[f"member_{score}"].astype(float), scores[f"nonmember_{score}"].astype(float)


def savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()


def format_audit_size_axis(ax: plt.Axes) -> None:
    ax.set_xscale("log")
    ax.set_xticks(AUDIT_SIZE_TICKS)
    ax.set_xticklabels([str(value) for value in AUDIT_SIZE_TICKS], rotation=0)


def build_summary_tables(metrics: pd.DataFrame, metadata: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    auc = metrics[metrics["metric"].eq("AUC")].copy()
    best_auc = (
        auc.sort_values("value", ascending=False)
        .groupby(["dataset", "model"], observed=True)
        .head(1)
        .loc[:, ["dataset", "model", "attack_score", "value"]]
        .rename(columns={"attack_score": "best_auc_score", "value": "best_auc"})
    )
    low = metrics[
        metrics["attack_score"].eq("neg_loss") & metrics["metric"].isin(["TPR@1%FPR", "TPR@0.1%FPR"])
    ].pivot_table(index=["dataset", "model"], columns="metric", values="value", observed=True).reset_index()
    summary = metadata.merge(best_auc, on=["dataset", "model"], how="left").merge(low, on=["dataset", "model"], how="left")
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
            "train_accuracy",
            "nonmember_accuracy",
            "accuracy_gap",
            "best_auc",
            "best_auc_score",
            "neg_loss_tpr_at_1pct_fpr",
            "neg_loss_tpr_at_0_1pct_fpr",
        ]
    ].sort_values(["dataset", "model"])
    summary_path = OUTPUT_DIR / "model_comparison_summary.csv"
    summary.to_csv(summary_path, index=False)

    markdown = summary.copy()
    for column in [
        "train_accuracy",
        "nonmember_accuracy",
        "accuracy_gap",
        "best_auc",
        "neg_loss_tpr_at_1pct_fpr",
        "neg_loss_tpr_at_0_1pct_fpr",
    ]:
        markdown[column] = markdown[column].map(lambda value: f"{value:.4f}")
    markdown["dataset"] = markdown["dataset"].map(DATASET_LABELS)
    markdown["model"] = markdown["model"].map(MODEL_LABELS)
    markdown["best_auc_score"] = markdown["best_auc_score"].map(SCORE_LABELS)
    md_path = OUTPUT_DIR / "model_comparison_summary.md"
    md_text = "# Model Comparison Summary\n\n"
    md_text += markdown.to_markdown(index=False)
    md_text += "\n"
    md_path.write_text(md_text, encoding="utf-8")

    width = metrics[metrics["metric"].eq("AUC")].copy()
    return summary, width


def plot_model_comparison_best_auc(summary: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "model_comparison_best_auc.png"
    plot_data = summary.copy()
    plot_data["dataset_label"] = plot_data["dataset"].map(DATASET_LABELS)
    plot_data["model_label"] = plot_data["model"].map(MODEL_LABELS)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    sns.barplot(
        data=plot_data,
        x="dataset_label",
        y="best_auc",
        hue="model_label",
        hue_order=[MODEL_LABELS[model] for model in MODEL_ORDER],
        palette=[MODEL_COLORS[model] for model in MODEL_ORDER],
        ax=ax,
    )
    ax.axhline(0.5, color="#3D3D3D", linewidth=1.1, linestyle="--", label="Random baseline")
    ax.set_ylim(0.45, 0.82)
    ax.set_xlabel("")
    ax.set_ylabel("Best attack AUC")
    ax.set_title("Best MIA AUC by dataset and target model")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.16))
    savefig(path)
    return path


def plot_target_gap_vs_best_auc(summary: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "target_gap_vs_best_auc.png"
    plot_data = summary.copy()
    plot_data["dataset_label"] = plot_data["dataset"].map(DATASET_LABELS)
    plot_data["model_label"] = plot_data["model"].map(MODEL_LABELS)

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    for model in MODEL_ORDER:
        subset = plot_data[plot_data["model"].eq(model)]
        ax.scatter(
            subset["accuracy_gap"],
            subset["best_auc"],
            s=105,
            color=MODEL_COLORS[model],
            edgecolor="white",
            linewidth=1.2,
            label=MODEL_LABELS[model],
        )
        for _, row in subset.iterrows():
            ax.annotate(
                DATASET_LABELS[row["dataset"]],
                (row["accuracy_gap"], row["best_auc"]),
                xytext=(6, 5),
                textcoords="offset points",
                fontsize=8.5,
            )
    ax.axhline(0.5, color="#3D3D3D", linewidth=1.0, linestyle="--")
    ax.set_xlabel("Train minus non-member accuracy")
    ax.set_ylabel("Best attack AUC")
    ax.set_title("Overfitting gap and membership signal")
    ax.legend(frameon=False, loc="lower right")
    savefig(path)
    return path


def plot_low_fpr_tpr(metrics: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "low_fpr_tpr_neg_loss.png"
    plot_data = metrics[
        metrics["attack_score"].eq("neg_loss") & metrics["metric"].isin(["TPR@1%FPR", "TPR@0.1%FPR"])
    ].copy()
    plot_data["dataset_label"] = plot_data["dataset"].map(DATASET_LABELS)
    plot_data["model_label"] = plot_data["model"].map(MODEL_LABELS)
    plot_data["metric_label"] = plot_data["metric"].map({"TPR@1%FPR": "TPR at 1% FPR", "TPR@0.1%FPR": "TPR at 0.1% FPR"})

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), sharey=False)
    for ax, metric in zip(axes, ["TPR@1%FPR", "TPR@0.1%FPR"], strict=True):
        subset = plot_data[plot_data["metric"].eq(metric)]
        sns.barplot(
            data=subset,
            x="dataset_label",
            y="value",
            hue="model_label",
            hue_order=[MODEL_LABELS[model] for model in MODEL_ORDER],
            palette=[MODEL_COLORS[model] for model in MODEL_ORDER],
            ax=ax,
        )
        baseline = 0.01 if metric == "TPR@1%FPR" else 0.001
        ax.axhline(baseline, color="#3D3D3D", linewidth=1.0, linestyle="--")
        ax.set_title("TPR at 1% FPR" if metric == "TPR@1%FPR" else "TPR at 0.1% FPR")
        ax.set_xlabel("")
        ax.set_ylabel("TPR")
        ax.legend_.remove()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.05))
    fig.suptitle("Low-FPR attack performance using negative loss", y=1.12)
    savefig(path)
    return path


def plot_low_fpr_roc() -> Path:
    path = OUTPUT_DIR / "low_fpr_roc_neg_loss.png"
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), sharey=True)
    max_tpr_in_region = 0.0
    for ax, dataset in zip(axes, DATASET_ORDER, strict=True):
        for model in MODEL_ORDER:
            member, nonmember = load_attack_scores(dataset, model, "neg_loss")
            y_true = np.concatenate([np.ones(member.size, dtype=int), np.zeros(nonmember.size, dtype=int)])
            scores = np.concatenate([member, nonmember])
            fpr, tpr, _ = roc_curve(y_true, scores)
            region_tpr = tpr[fpr <= 0.05]
            if region_tpr.size:
                max_tpr_in_region = max(max_tpr_in_region, float(region_tpr.max()))
            ax.plot(
                fpr,
                tpr,
                color=MODEL_COLORS[model],
                linewidth=2.0,
                label=MODEL_LABELS[model],
            )
        ax.plot([0, 0.05], [0, 0.05], color="#777777", linestyle="--", linewidth=1.0)
        ax.set_xlim(0, 0.05)
        ax.set_title(DATASET_LABELS[dataset])
        ax.set_xlabel("False positive rate")
        ax.grid(True, axis="both", linewidth=0.5, alpha=0.25)
    y_max = min(1.0, max(0.30, max_tpr_in_region * 1.12))
    for ax in axes:
        ax.set_ylim(0, y_max)
    axes[0].set_ylabel("True positive rate")
    axes[1].legend(frameon=False, loc="upper right")
    fig.suptitle("Low-FPR ROC region for negative-loss attack scores", y=1.03)
    savefig(path)
    return path


def plot_audit_size_tpr_mean(sensitivity: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "audit_size_tpr_mean_neg_loss.png"
    plot_data = sensitivity[
        sensitivity["attack_score"].eq("neg_loss") & sensitivity["metric"].isin(["TPR@1%FPR", "TPR@0.1%FPR"])
    ].copy()
    plot_data["model_label"] = plot_data["model"].map(MODEL_LABELS)

    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.0), sharex=True)
    for row_idx, dataset in enumerate(DATASET_ORDER):
        for col_idx, metric in enumerate(["TPR@1%FPR", "TPR@0.1%FPR"]):
            ax = axes[row_idx, col_idx]
            subset = plot_data[plot_data["dataset"].eq(dataset) & plot_data["metric"].eq(metric)]
            for model in MODEL_ORDER:
                model_subset = subset[subset["model"].eq(model)].sort_values("sample_size")
                ax.plot(
                    model_subset["sample_size"],
                    model_subset["mean"],
                    color=MODEL_COLORS[model],
                    marker="o",
                    linewidth=1.8,
                    label=MODEL_LABELS[model],
                )
            baseline = 0.01 if metric == "TPR@1%FPR" else 0.001
            ax.axhline(baseline, color="#555555", linewidth=1.0, linestyle="--")
            ax.set_title(f"{DATASET_LABELS[dataset]} - {metric}")
            format_audit_size_axis(ax)
            ax.set_xlabel("Audit sample size per class")
            ax.set_ylabel("Mean TPR")
            ax.grid(True, axis="both", linewidth=0.5, alpha=0.25)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.02))
    fig.suptitle("Mean low-FPR TPR under repeated audit subsampling", y=1.08)
    savefig(path)
    return path


def plot_audit_size_widths(sensitivity: pd.DataFrame, metric: str, filename: str, title: str, ylabel: str) -> Path:
    path = OUTPUT_DIR / filename
    plot_data = sensitivity[sensitivity["attack_score"].eq("neg_loss") & sensitivity["metric"].eq(metric)].copy()

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8), sharey=True)
    for ax, dataset in zip(axes, DATASET_ORDER, strict=True):
        subset = plot_data[plot_data["dataset"].eq(dataset)]
        for model in MODEL_ORDER:
            model_subset = subset[subset["model"].eq(model)].sort_values("sample_size")
            ax.plot(
                model_subset["sample_size"],
                model_subset["interval_width"],
                color=MODEL_COLORS[model],
                marker="o",
                linewidth=1.8,
                label=MODEL_LABELS[model],
            )
        ax.set_title(DATASET_LABELS[dataset])
        format_audit_size_axis(ax)
        ax.set_xlabel("Audit sample size per class")
        ax.set_ylabel(ylabel)
        ax.grid(True, axis="both", linewidth=0.5, alpha=0.25)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.05))
    fig.suptitle(title, y=1.12)
    savefig(path)
    return path


def plot_score_distribution(dataset: str, model: str, score: str) -> Path:
    path = OUTPUT_DIR / f"score_distribution_{dataset}_{model}_{score}.png"
    member, nonmember = load_attack_scores(dataset, model, score)
    rng = np.random.default_rng(20260602)
    max_points = 50000
    if member.size > max_points:
        member = rng.choice(member, size=max_points, replace=False)
    if nonmember.size > max_points:
        nonmember = rng.choice(nonmember, size=max_points, replace=False)
    combined = np.concatenate([member, nonmember])
    lower, upper = np.quantile(combined, [0.005, 0.995])
    frame = pd.DataFrame(
        {
            "score": np.concatenate([member, nonmember]),
            "group": ["Member"] * member.size + ["Non-member"] * nonmember.size,
        }
    )

    fig, ax = plt.subplots(figsize=(8.2, 4.9))
    sns.histplot(
        data=frame,
        x="score",
        hue="group",
        hue_order=["Member", "Non-member"],
        palette=MEMBERSHIP_COLORS,
        bins=70,
        stat="density",
        common_norm=False,
        alpha=0.42,
        element="step",
        ax=ax,
    )
    ax.set_xlim(lower, upper)
    ax.set_xlabel(SCORE_LABELS[score])
    ax.set_ylabel("Density")
    ax.set_title(f"{DATASET_LABELS[dataset]} {MODEL_LABELS[model]} score distributions")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.25)
    legend = ax.get_legend()
    if legend is not None:
        legend.set_title("Membership")
    savefig(path)
    return path


def write_captions(paths: list[Path]) -> Path:
    caption_path = FIGURE_ROOT / "figure_captions.md"
    relative = {path.name: path.relative_to(PROJECT_ROOT) for path in paths}
    text = """# Figure Captions

Generated from `05_analysis/generate_figures.py` using the `core` and `model_extension_hgb` result folders.

## Diagnostic Figures

**model_comparison_best_auc.png**: Best membership-inference AUC for each dataset and target model, selecting the strongest of the four simple attack scores. The dashed line marks random guessing. Random forest produces the strongest MIA signal, while logistic regression and HistGradientBoosting remain near random.

**target_gap_vs_best_auc.png**: Relationship between the target model train/non-member accuracy gap and the best MIA AUC. The plot supports the interpretation that overfitting, rather than predictive accuracy alone, drives the observed simple-score MIA signal.

**low_fpr_roc_neg_loss.png**: Low-FPR region of ROC curves for the negative-loss attack score. This view emphasizes the operating range most relevant for privacy auditing and shows that non-random AUC does not necessarily imply large TPR at very low FPR.

**low_fpr_tpr_neg_loss.png**: TPR at 1% FPR and 0.1% FPR for the negative-loss attack score. Baseline lines mark the corresponding FPR levels, helping show whether the attack meaningfully exceeds random low-FPR behavior.

**audit_size_tpr_mean_neg_loss.png**: Mean low-FPR TPR under repeated balanced audit subsampling. The figure shows how reported low-FPR performance changes when only a finite number of member and non-member audit records are available.

**audit_size_auc_width_neg_loss.png**: Empirical 95% interval width for AUC under repeated audit subsampling. Interval widths shrink as audit sample size increases, supporting the paper's finite-sample uncertainty argument.

**audit_size_tpr001_width_neg_loss.png**: Empirical 95% interval width for TPR at 0.1% FPR under repeated audit subsampling. The smallest audit sizes are especially fragile because the expected number of false positives is below one.

**score_distribution_credit_default_random_forest_neg_loss.png**: Member and non-member negative-loss score distributions for the credit-default random forest. The x-axis is limited to the central 99% of sampled scores for readability.

"""
    text += "## File Locations\n\n"
    for name in sorted(relative):
        text += f"- `{name}`: `{relative[name]}`\n"
    caption_path.write_text(text, encoding="utf-8")
    return caption_path


def main() -> None:
    sns.set_theme(style="whitegrid", context="paper")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metrics = load_main_metrics()
    sensitivity = load_subsampling()
    metadata = load_model_metadata()
    summary, _ = build_summary_tables(metrics, metadata)

    paths = [
        plot_model_comparison_best_auc(summary),
        plot_target_gap_vs_best_auc(summary),
        plot_low_fpr_roc(),
        plot_low_fpr_tpr(metrics),
        plot_audit_size_tpr_mean(sensitivity),
        plot_audit_size_widths(
            sensitivity,
            metric="AUC",
            filename="audit_size_auc_width_neg_loss.png",
            title="AUC interval width under repeated audit subsampling",
            ylabel="Empirical 95% interval width",
        ),
        plot_audit_size_widths(
            sensitivity,
            metric="TPR@0.1%FPR",
            filename="audit_size_tpr001_width_neg_loss.png",
            title="TPR at 0.1% FPR interval width under repeated audit subsampling",
            ylabel="Empirical 95% interval width",
        ),
        plot_score_distribution("credit_default", "random_forest", "neg_loss"),
    ]
    caption_path = write_captions(paths)

    print("Generated figures:")
    for path in paths:
        print(f"- {path.relative_to(PROJECT_ROOT)}")
    print(f"Generated captions: {caption_path.relative_to(PROJECT_ROOT)}")
    print(f"Generated summary table: {(OUTPUT_DIR / 'model_comparison_summary.csv').relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
