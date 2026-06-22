#!/usr/bin/env python3
"""Generate compact appendix figures for the Q1 manuscript.

These figures visualize already-generated appendix CSV outputs; they do not run
new experiments.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "09_final" / "manuscript_package" / "figures"
PNG_DIR = FIG_DIR / "flattened"
VEC_DIR = FIG_DIR / "vector"


def _save(fig: plt.Figure, name: str) -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    VEC_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in [
        (".png", {"dpi": 300}),
        (".pdf", {}),
        (".svg", {}),
    ]:
        out = (PNG_DIR if suffix == ".png" else VEC_DIR) / f"{name}{suffix}"
        fig.savefig(out, bbox_inches="tight", facecolor="white", **kwargs)


def plot_shadow_summary() -> None:
    path = ROOT / "05_analysis" / "results" / "q1_lira_like_appendix" / "tables" / "key_metrics.csv"
    df = pd.read_csv(path)
    df["setting"] = df["dataset"].map({"credit_default": "CD/RF", "adult_income": "Adult/RF"})
    df["source"] = df["score_source"].map({
        "target_base_neg_loss": "target",
        "bounded_shadow_lira_like": "shadow",
    })
    metrics = [("AUC", "AUC"), ("TPR@1%FPR", "TPR@1%"), ("TPR@0.1%FPR", "TPR@0.1%")]
    colors = {"target": "#3B6EA8", "shadow": "#C65A3A"}

    fig, axes = plt.subplots(3, 1, figsize=(3.35, 4.25), sharey=False)
    for ax, (col, label) in zip(axes, metrics):
        x = np.arange(2)
        width = 0.34
        for offset, source in [(-width / 2, "target"), (width / 2, "shadow")]:
            vals = [
                df[(df["setting"] == setting) & (df["source"] == source)][col].iloc[0]
                for setting in ["CD/RF", "Adult/RF"]
            ]
            ax.bar(x + offset, vals, width=width, color=colors[source], label=source)
        ax.set_title(label, fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(["CD/RF", "Adult/RF"], fontsize=7)
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(axis="y", color="#d9d9d9", linewidth=0.5)
        ax.set_ylim(0, 1.0 if col == "AUC" else max(0.055, df[col].max() * 1.25))
    axes[0].legend(frameon=False, fontsize=7, loc="upper right")
    fig.suptitle("Bounded shadow score summary", fontsize=9, y=1.01)
    fig.tight_layout(pad=0.55, h_pad=0.65)
    _save(fig, "q1_appendix_shadow_score_summary")
    plt.close(fig)


def plot_tie_rule_summary() -> None:
    path = ROOT / "05_analysis" / "results" / "q1_tie_rule_sensitivity" / "paper_table_tie_rule_sensitivity.csv"
    df = pd.read_csv(path)
    df = df[df["target_fpr"].round(3) == 0.001].copy()
    settings = df["setting"].tolist()
    x = np.arange(len(settings))
    width = 0.24
    series = [
        ("strict_tpr", "strict", "#777777"),
        ("randomized_tpr", "randomized", "#3B6EA8"),
        ("inclusive_tpr", "inclusive", "#C65A3A"),
    ]

    fig, ax = plt.subplots(figsize=(3.45, 2.4))
    for i, (col, label, color) in enumerate(series):
        ax.bar(x + (i - 1) * width, df[col], width=width, color=color, label=label)
    ax.set_xticks(x)
    ax.set_xticklabels(settings, fontsize=7)
    ax.set_ylabel("TPR at 0.1% FPR", fontsize=8)
    ax.tick_params(axis="y", labelsize=7)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.5)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.set_title("Tie-rule sensitivity at the tail", fontsize=9)
    fig.tight_layout(pad=0.5)
    _save(fig, "q1_appendix_tie_rule_summary")
    plt.close(fig)


def plot_split_seed_summary() -> None:
    path = ROOT / "05_analysis" / "results" / "q1_split_seed_sensitivity" / "paper_table_split_seed_sensitivity.csv"
    df = pd.read_csv(path)
    settings = df["setting"].tolist()
    metrics = [
        ("auc_mean", "auc_min", "auc_max", "AUC", "#3B6EA8"),
        ("tpr1_mean", "tpr1_min", "tpr1_max", "TPR@1%", "#5B8E3E"),
        ("tpr001_mean", "tpr001_min", "tpr001_max", "TPR@0.1%", "#C65A3A"),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(3.35, 4.05))
    y = np.arange(len(settings))
    for ax, (mean_col, min_col, max_col, label, color) in zip(axes, metrics):
        means = df[mean_col].to_numpy()
        mins = df[min_col].to_numpy()
        maxs = df[max_col].to_numpy()
        xerr = np.vstack([means - mins, maxs - means])
        ax.errorbar(means, y, xerr=xerr, fmt="o", color=color, ecolor=color, capsize=3, markersize=4)
        ax.set_title(label, fontsize=8)
        ax.set_yticks(y)
        ax.set_yticklabels(settings, fontsize=7)
        ax.tick_params(axis="x", labelsize=7)
        ax.grid(axis="x", color="#d9d9d9", linewidth=0.5)
        if label == "AUC":
            ax.set_xlim(0.60, 1.01)
        elif label == "TPR@1%":
            ax.set_xlim(0, 1.02)
        else:
            ax.set_xlim(0, 0.42)
    axes[0].invert_yaxis()
    fig.suptitle("Split/seed mean and range over five repeats", fontsize=9, y=1.01)
    fig.tight_layout(pad=0.5, h_pad=0.55)
    _save(fig, "q1_appendix_split_seed_summary")
    plt.close(fig)


def main() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.7,
    })
    plot_shadow_summary()
    plot_tie_rule_summary()
    plot_split_seed_summary()


if __name__ == "__main__":
    main()
