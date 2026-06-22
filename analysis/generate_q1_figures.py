from __future__ import annotations

from pathlib import Path

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


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "figures_tables" / "q1"
REFERENCE_CENTERED_DIR = PROJECT_ROOT / "analysis" / "results" / "q1_stronger_score_appendix"
LABEL_STRESS_DIR = (
    PROJECT_ROOT
    / "analysis"
    / "results"
    / "q1_label_uncertainty_stress"
    / "credit_default_random_forest_neg_loss"
)
BASELINE_CI_PATH = (
    PROJECT_ROOT
    / "figures_tables"
    / "appendix_tables"
    / "appendix_table_a2_stage1_confidence_intervals.csv"
)

SETTING_ORDER = ["credit_default", "adult_income"]
SETTING_LABELS = {
    "credit_default": "Credit Default\nRandom Forest",
    "adult_income": "Adult Income\nRandom Forest",
}
SCORE_ORDER = ["neg_loss", "ref_centered_neg_loss", "ref_logit_margin", "ref_z_logit_margin"]
SCORE_LABELS = {
    "neg_loss": "Baseline\nneg_loss",
    "ref_centered_neg_loss": "Ref-centered\nneg_loss",
    "ref_logit_margin": "Ref logit\nmargin",
    "ref_z_logit_margin": "Ref z-logit\nmargin",
}
SCORE_COLORS = {
    "neg_loss": "#4C78A8",
    "ref_centered_neg_loss": "#59A14F",
    "ref_logit_margin": "#F28E2B",
    "ref_z_logit_margin": "#E15759",
}
METRIC_LABELS = {
    "AUC": "AUC",
    "TPR@1%FPR": "TPR@1%FPR",
    "TPR@0.1%FPR": "TPR@0.1%FPR",
}
CORRUPTION_LEVELS = [0.0, 0.005, 0.01, 0.02, 0.05]
CORRUPTION_LABELS = ["0", "0.5", "1", "2", "5"]
STRESS_METRICS = ["AUC", "TPR@1%FPR", "TPR@0.1%FPR"]
STRESS_COLORS = {
    "AUC": "#4C78A8",
    "TPR@1%FPR": "#E15759",
    "TPR@0.1%FPR": "#59A14F",
}


def savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.gcf()
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(path, dpi=400, bbox_inches="tight")
    plt.close(fig)


def load_reference_centered_metrics() -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for setting in ["credit_default_random_forest", "adult_income_random_forest"]:
        dataset = setting.replace("_random_forest", "")
        metrics = pd.read_csv(REFERENCE_CENTERED_DIR / setting / "comparison_metrics.csv")
        metrics["metric"] = metrics["metric"].replace(
            {
                "TPR@0.01FPR": "TPR@1%FPR",
                "TPR@0.001FPR": "TPR@0.1%FPR",
            }
        )
        metrics["dataset"] = dataset
        rows.append(metrics)

    reference_centered = pd.concat(rows, ignore_index=True)
    reference_centered = reference_centered[reference_centered["metric"].isin(METRIC_LABELS)]

    baseline_ci = pd.read_csv(BASELINE_CI_PATH)
    baseline_ci = baseline_ci[
        (baseline_ci["dataset"].isin(SETTING_ORDER))
        & (baseline_ci["model"] == "random_forest")
        & (baseline_ci["attack_score"] == "neg_loss")
        & (baseline_ci["metric"].isin(METRIC_LABELS))
    ].copy()
    baseline_ci["score_source"] = "simple_score_baseline"

    reference_centered_ci_rows: list[pd.DataFrame] = []
    for setting in ["credit_default_random_forest", "adult_income_random_forest"]:
        ci = pd.read_csv(REFERENCE_CENTERED_DIR / setting / "audit_tool" / "metrics" / "confidence_intervals.csv")
        ci["dataset"] = setting.replace("_random_forest", "")
        reference_centered_ci_rows.append(ci)
    reference_centered_ci = pd.concat(reference_centered_ci_rows, ignore_index=True)
    reference_centered_ci = reference_centered_ci[reference_centered_ci["metric"].isin(METRIC_LABELS)]

    ci = pd.concat(
        [
            baseline_ci.loc[
                :,
                ["dataset", "attack_score", "metric", "point", "ci_lower", "ci_upper"],
            ],
            reference_centered_ci.loc[
                :,
                ["dataset", "attack_score", "metric", "point", "ci_lower", "ci_upper"],
            ],
        ],
        ignore_index=True,
    )

    merged = reference_centered.merge(ci, on=["dataset", "attack_score", "metric"], how="left")
    merged["dataset"] = pd.Categorical(merged["dataset"], SETTING_ORDER, ordered=True)
    merged["attack_score"] = pd.Categorical(merged["attack_score"], SCORE_ORDER, ordered=True)
    return merged.sort_values(["dataset", "attack_score", "metric"]).reset_index(drop=True)


def plot_reference_centered_score_figure(metrics: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "q1_reference_centered_score_compatibility.png"
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.9))
    x_positions = list(range(len(SETTING_ORDER)))
    width = 0.18
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]

    for panel_idx, metric in enumerate(["AUC", "TPR@1%FPR", "TPR@0.1%FPR"]):
        ax = axes[panel_idx]
        subset = metrics[metrics["metric"] == metric]
        for score_idx, score in enumerate(SCORE_ORDER):
            score_subset = subset[subset["attack_score"] == score]
            xs = [x + offsets[score_idx] for x in x_positions]
            ys = [
                float(
                    score_subset[score_subset["dataset"] == dataset]["value"].iloc[0]
                )
                for dataset in SETTING_ORDER
            ]
            if metric == "TPR@0.1%FPR":
                lowers = [
                    float(
                        score_subset[score_subset["dataset"] == dataset]["ci_lower"].iloc[0]
                    )
                    for dataset in SETTING_ORDER
                ]
                uppers = [
                    float(
                        score_subset[score_subset["dataset"] == dataset]["ci_upper"].iloc[0]
                    )
                    for dataset in SETTING_ORDER
                ]
                yerr = [
                    [y - low for y, low in zip(ys, lowers)],
                    [high - y for y, high in zip(ys, uppers)],
                ]
                ax.errorbar(
                    xs,
                    ys,
                    yerr=yerr,
                    fmt="o",
                    color=SCORE_COLORS[score],
                    ecolor=SCORE_COLORS[score],
                    elinewidth=1.0,
                    capsize=2,
                    markersize=4.2,
                    label=SCORE_LABELS[score],
                )
            else:
                ax.bar(
                    xs,
                    ys,
                    width=width,
                    color=SCORE_COLORS[score],
                    label=SCORE_LABELS[score],
                )

        ax.set_xticks(x_positions)
        ax.set_xticklabels([SETTING_LABELS[dataset] for dataset in SETTING_ORDER])
        ax.set_title(METRIC_LABELS[metric])
        ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.35)
        if metric == "AUC":
            ax.set_ylim(0.55, 0.98)
        elif metric == "TPR@1%FPR":
            ax.set_ylim(0.0, 0.42)
        else:
            ax.set_ylim(0.0, 0.07)

    axes[0].set_ylabel("Metric value")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.06), fontsize=7)
    fig.suptitle(
        "Reference-centered score-array compatibility: low-FPR uncertainty remains",
        y=1.10,
        fontsize=10,
    )
    fig.tight_layout()
    savefig(path)
    return path


def load_label_stress_summary() -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = pd.read_csv(LABEL_STRESS_DIR / "tables" / "label_uncertainty_summary.csv")
    summary = summary[summary["metric"].isin(STRESS_METRICS)].copy()

    ci_rows: list[pd.DataFrame] = []
    for rate in CORRUPTION_LEVELS:
        tag = f"{rate:.3f}".replace(".", "p")
        ci = pd.read_csv(
            LABEL_STRESS_DIR / "audit_tool" / f"corruption_{tag}" / "metrics" / "confidence_intervals.csv"
        )
        ci["corruption_rate"] = rate
        ci_rows.append(ci)
    canonical = pd.concat(ci_rows, ignore_index=True)
    canonical = canonical[canonical["metric"].isin(STRESS_METRICS)].copy()
    return summary, canonical


def plot_label_uncertainty_figure(summary: pd.DataFrame, canonical: pd.DataFrame) -> Path:
    path = OUTPUT_DIR / "q1_label_uncertainty_degradation.png"
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.8), sharex=True)

    for idx, metric in enumerate(STRESS_METRICS):
        ax = axes[idx]
        metric_summary = summary[summary["metric"] == metric].sort_values("corruption_rate")
        metric_canonical = canonical[canonical["metric"] == metric].sort_values("corruption_rate")
        x = [rate * 100 for rate in metric_summary["corruption_rate"]]
        mean = metric_summary["mean"].tolist()
        lower = metric_summary["p025"].tolist()
        upper = metric_summary["p975"].tolist()
        point = metric_canonical["point"].tolist()
        ci_lower = metric_canonical["ci_lower"].tolist()
        ci_upper = metric_canonical["ci_upper"].tolist()

        ax.fill_between(x, lower, upper, color=STRESS_COLORS[metric], alpha=0.18)
        ax.plot(x, mean, color=STRESS_COLORS[metric], linewidth=1.8, marker="o", markersize=3.5)
        ax.errorbar(
            x,
            point,
            yerr=[
                [p - low for p, low in zip(point, ci_lower)],
                [high - p for p, high in zip(point, ci_upper)],
            ],
            fmt="o",
            color="black",
            ecolor="black",
            elinewidth=0.9,
            capsize=2,
            markersize=3.0,
        )

        ax.set_title(METRIC_LABELS[metric])
        ax.set_xticks([0, 0.5, 1, 2, 5])
        ax.set_xticklabels(CORRUPTION_LABELS)
        ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.35)
        if metric == "AUC":
            ax.set_ylim(0.725, 0.765)
        elif metric == "TPR@1%FPR":
            ax.set_ylim(0.034, 0.0515)
        else:
            ax.set_ylim(0.0025, 0.0056)

    axes[0].set_ylabel("Metric value")
    axes[1].set_xlabel("Symmetric audit-label corruption rate (%)")
    fig.suptitle(
        "Audit-label uncertainty degrades reported signal but not the need for intervals",
        y=1.06,
        fontsize=10,
    )
    fig.tight_layout()
    savefig(path)
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reference_centered_metrics = load_reference_centered_metrics()
    summary, canonical = load_label_stress_summary()
    reference_centered_path = plot_reference_centered_score_figure(reference_centered_metrics)
    stress_path = plot_label_uncertainty_figure(summary, canonical)
    readme = (
        "# Q1 Figures\n\n"
        "Generated from existing Q1 result folders without rerunning experiments.\n\n"
        f"- `{reference_centered_path.relative_to(PROJECT_ROOT)}`: reference-centered score-array compatibility figure.\n"
        f"- `{stress_path.relative_to(PROJECT_ROOT)}`: label-uncertainty degradation figure.\n"
    )
    (OUTPUT_DIR / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
