from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPANDED_RUN = "expanded_tabular_stage1"
EXPANDED_RESULTS = PROJECT_ROOT / "05_analysis" / "results" / EXPANDED_RUN
HARDENED_RESULTS = PROJECT_ROOT / "05_analysis" / "results" / "final_ci_hardening"
EXPANDED_TABLES = PROJECT_ROOT / "06_figures_tables" / "expanded"
FINAL_TABLE_DIR = PROJECT_ROOT / "06_figures_tables" / "final_tables"
APPENDIX_TABLE_DIR = PROJECT_ROOT / "06_figures_tables" / "appendix_tables"

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
DATASET_TASKS = {
    "credit_default": "Default payment prediction",
    "covertype": "Forest cover type classification",
    "adult_income": "Income threshold prediction",
    "bank_marketing": "Term-deposit subscription prediction",
    "diabetes_readmission": "Early readmission prediction",
}
MODEL_ORDER = [
    "logistic_regression",
    "hist_gradient_boosting",
    "random_forest",
    "extra_trees",
    "small_mlp",
]
MODEL_LABELS = {
    "logistic_regression": "Logistic regression",
    "hist_gradient_boosting": "HistGradientBoosting",
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
FPR_LABELS = {
    0.01: "1% FPR",
    0.001: "0.1% FPR",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def label_dataset(value: str) -> str:
    return DATASET_LABELS.get(str(value), str(value))


def label_model(value: str) -> str:
    return MODEL_LABELS.get(str(value), str(value))


def label_score(value: str) -> str:
    return SCORE_LABELS.get(str(value), str(value))


def fmt_num(value: object, digits: int = 4) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def fmt_count(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{int(value):,}"


def fmt_ci(point: object, lower: object, upper: object, digits: int = 4) -> str:
    if pd.isna(point) or pd.isna(lower) or pd.isna(upper):
        return ""
    return f"{float(point):.{digits}f} [{float(lower):.{digits}f}, {float(upper):.{digits}f}]"


def write_markdown_table(path: Path, title: str, note: str, table: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"# {title}\n\n"
    if note:
        text += f"{note}\n\n"
    text += table.to_markdown(index=False)
    text += "\n"
    path.write_text(text, encoding="utf-8")


def load_model_metadata() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for dataset in DATASET_ORDER:
        path = EXPANDED_RESULTS / "models" / dataset / "logistic_regression" / "metadata.json"
        metadata = read_json(path)
        rows.append(
            {
                "dataset": dataset,
                "task": DATASET_TASKS[dataset],
                "n_rows": metadata["n_rows"],
                "n_features": metadata["n_features"],
                "n_classes": len(metadata["labels"]),
                "n_members": metadata["member_pool_size"],
                "n_nonmembers": metadata["nonmember_pool_size"],
                "split_rule": "50% member / 50% non-member audit split",
            }
        )
    return pd.DataFrame(rows)


def load_summary() -> pd.DataFrame:
    summary = pd.read_csv(EXPANDED_TABLES / "expanded_model_comparison_summary.csv")
    summary["dataset"] = pd.Categorical(summary["dataset"], DATASET_ORDER, ordered=True)
    summary["model"] = pd.Categorical(summary["model"], MODEL_ORDER, ordered=True)
    return summary.sort_values(["dataset", "model"]).reset_index(drop=True)


def load_hardened() -> pd.DataFrame:
    hardened = pd.read_csv(HARDENED_RESULTS / "hardened_confidence_intervals.csv")
    hardened["dataset"] = pd.Categorical(hardened["dataset"], DATASET_ORDER, ordered=True)
    hardened["model"] = pd.Categorical(hardened["model"], MODEL_ORDER, ordered=True)
    return hardened.sort_values(["dataset", "model", "attack_score", "metric"]).reset_index(drop=True)


def ci_lookup(hardened: pd.DataFrame, dataset: str, model: str, score: str, metric: str) -> dict[str, object]:
    rows = hardened[
        hardened["dataset"].astype(str).eq(dataset)
        & hardened["model"].astype(str).eq(model)
        & hardened["attack_score"].eq(score)
        & hardened["metric"].eq(metric)
    ]
    if rows.empty:
        return {"point": pd.NA, "ci_lower": pd.NA, "ci_upper": pd.NA, "ci_width": pd.NA, "n_bootstrap": pd.NA}
    row = rows.iloc[0]
    return {
        "point": row["point"],
        "ci_lower": row["ci_lower"],
        "ci_upper": row["ci_upper"],
        "ci_width": row["ci_width"],
        "n_bootstrap": row["n_bootstrap"],
    }


def build_dataset_table() -> pd.DataFrame:
    table = load_model_metadata()
    table.to_csv(FINAL_TABLE_DIR / "table1_dataset_split_summary.csv", index=False)

    md = table.copy()
    md["dataset"] = md["dataset"].map(label_dataset)
    for column in ["n_rows", "n_features", "n_classes", "n_members", "n_nonmembers"]:
        md[column] = md[column].map(fmt_count)
    md = md.rename(
        columns={
            "dataset": "Dataset",
            "task": "Prediction task",
            "n_rows": "Rows",
            "n_features": "Features",
            "n_classes": "Classes",
            "n_members": "Members",
            "n_nonmembers": "Non-members",
            "split_rule": "Audit split",
        }
    )
    write_markdown_table(
        FINAL_TABLE_DIR / "table1_dataset_split_summary.md",
        "Table 1. Dataset and audit-split summary",
        "Source: logistic-regression metadata from `expanded_tabular_stage1`; the split is identical across target models.",
        md,
    )
    return table


def build_model_comparison_table(summary: pd.DataFrame) -> pd.DataFrame:
    table = summary[
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
    ].copy()
    table.to_csv(FINAL_TABLE_DIR / "table2_model_comparison.csv", index=False)

    md = table.copy()
    md["dataset"] = md["dataset"].astype(str).map(label_dataset)
    md["model"] = md["model"].astype(str).map(label_model)
    md["best_auc_score"] = md["best_auc_score"].map(label_score)
    for column in ["n_members", "n_nonmembers", "n_features"]:
        md[column] = md[column].map(fmt_count)
    for column in [
        "train_accuracy",
        "nonmember_accuracy",
        "accuracy_gap",
        "best_auc",
        "neg_loss_tpr_at_1pct_fpr",
        "neg_loss_tpr_at_0_1pct_fpr",
    ]:
        md[column] = md[column].map(fmt_num)
    md = md.rename(
        columns={
            "dataset": "Dataset",
            "model": "Model",
            "n_members": "Members",
            "n_nonmembers": "Non-members",
            "n_features": "Features",
            "train_accuracy": "Train acc.",
            "nonmember_accuracy": "Non-member acc.",
            "accuracy_gap": "Acc. gap",
            "best_auc": "Best AUC",
            "best_auc_score": "Best-AUC score",
            "neg_loss_tpr_at_1pct_fpr": "Neg-loss TPR@1%FPR",
            "neg_loss_tpr_at_0_1pct_fpr": "Neg-loss TPR@0.1%FPR",
        }
    )
    write_markdown_table(
        FINAL_TABLE_DIR / "table2_model_comparison.md",
        "Table 2. Model comparison and point-estimate MIA signal",
        "Source: `06_figures_tables/expanded/expanded_model_comparison_summary.csv`; point estimates are descriptive.",
        md,
    )
    return table


def build_main_mia_table(summary: pd.DataFrame, hardened: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in summary.iterrows():
        dataset = str(row["dataset"])
        model = str(row["model"])
        best_score = str(row["best_auc_score"])
        best_auc = ci_lookup(hardened, dataset, model, best_score, "AUC")
        tpr_1 = ci_lookup(hardened, dataset, model, "neg_loss", "TPR@1%FPR")
        tpr_01 = ci_lookup(hardened, dataset, model, "neg_loss", "TPR@0.1%FPR")
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "best_auc_score": best_score,
                "best_auc": best_auc["point"],
                "best_auc_ci_lower": best_auc["ci_lower"],
                "best_auc_ci_upper": best_auc["ci_upper"],
                "best_auc_ci_width": best_auc["ci_width"],
                "neg_loss_tpr_1pct": tpr_1["point"],
                "neg_loss_tpr_1pct_ci_lower": tpr_1["ci_lower"],
                "neg_loss_tpr_1pct_ci_upper": tpr_1["ci_upper"],
                "neg_loss_tpr_1pct_ci_width": tpr_1["ci_width"],
                "neg_loss_tpr_0_1pct": tpr_01["point"],
                "neg_loss_tpr_0_1pct_ci_lower": tpr_01["ci_lower"],
                "neg_loss_tpr_0_1pct_ci_upper": tpr_01["ci_upper"],
                "neg_loss_tpr_0_1pct_ci_width": tpr_01["ci_width"],
                "n_bootstrap": best_auc["n_bootstrap"],
                "n_members": row["n_members"],
                "n_nonmembers": row["n_nonmembers"],
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(FINAL_TABLE_DIR / "table3_main_mia_metrics_hardened.csv", index=False)

    md = table.copy()
    md["Dataset"] = md["dataset"].map(label_dataset)
    md["Model"] = md["model"].map(label_model)
    md["Best-AUC score"] = md["best_auc_score"].map(label_score)
    md["Best AUC, 95% CI"] = md.apply(
        lambda item: fmt_ci(item["best_auc"], item["best_auc_ci_lower"], item["best_auc_ci_upper"]),
        axis=1,
    )
    md["Neg-loss TPR@1%FPR, 95% CI"] = md.apply(
        lambda item: fmt_ci(
            item["neg_loss_tpr_1pct"],
            item["neg_loss_tpr_1pct_ci_lower"],
            item["neg_loss_tpr_1pct_ci_upper"],
        ),
        axis=1,
    )
    md["Neg-loss TPR@0.1%FPR, 95% CI"] = md.apply(
        lambda item: fmt_ci(
            item["neg_loss_tpr_0_1pct"],
            item["neg_loss_tpr_0_1pct_ci_lower"],
            item["neg_loss_tpr_0_1pct_ci_upper"],
        ),
        axis=1,
    )
    md["Members"] = md["n_members"].map(fmt_count)
    md["Non-members"] = md["n_nonmembers"].map(fmt_count)
    md = md[
        [
            "Dataset",
            "Model",
            "Best-AUC score",
            "Best AUC, 95% CI",
            "Neg-loss TPR@1%FPR, 95% CI",
            "Neg-loss TPR@0.1%FPR, 95% CI",
            "Members",
            "Non-members",
        ]
    ]
    write_markdown_table(
        FINAL_TABLE_DIR / "table3_main_mia_metrics_hardened.md",
        "Table 3. Main MIA metrics with hardened bootstrap intervals",
        "Source: `final_ci_hardening/hardened_confidence_intervals.csv`; intervals use 1,000 stratified bootstrap repeats.",
        md,
    )
    return table


def build_uncertainty_summary(hardened: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for metric, group in hardened.groupby("metric", sort=False):
        widest = group.sort_values("ci_width", ascending=False).iloc[0]
        rows.append(
            {
                "metric": metric,
                "n_rows": len(group),
                "median_ci_width": group["ci_width"].median(),
                "p75_ci_width": group["ci_width"].quantile(0.75),
                "max_ci_width": group["ci_width"].max(),
                "widest_dataset": str(widest["dataset"]),
                "widest_model": str(widest["model"]),
                "widest_attack_score": widest["attack_score"],
                "widest_score_role": widest["score_role"],
                "n_bootstrap": int(group["n_bootstrap"].max()),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(FINAL_TABLE_DIR / "table4_uncertainty_summary.csv", index=False)

    md = table.copy()
    md["widest_dataset"] = md["widest_dataset"].map(label_dataset)
    md["widest_model"] = md["widest_model"].map(label_model)
    md["widest_attack_score"] = md["widest_attack_score"].map(label_score)
    for column in ["median_ci_width", "p75_ci_width", "max_ci_width"]:
        md[column] = md[column].map(fmt_num)
    md = md.rename(
        columns={
            "metric": "Metric",
            "n_rows": "Rows",
            "median_ci_width": "Median CI width",
            "p75_ci_width": "75th pct. CI width",
            "max_ci_width": "Max CI width",
            "widest_dataset": "Widest row dataset",
            "widest_model": "Widest row model",
            "widest_attack_score": "Widest row score",
            "widest_score_role": "Score role",
            "n_bootstrap": "Bootstrap repeats",
        }
    )
    write_markdown_table(
        FINAL_TABLE_DIR / "table4_uncertainty_summary.md",
        "Table 4. Hardened interval-width summary",
        "Source: selected main-table rows in `final_ci_hardening`; this table summarizes uncertainty, not model superiority.",
        md,
    )
    return table


def warning_label(expected_false_positives: float) -> str:
    if expected_false_positives < 1:
        return "severe"
    if expected_false_positives < 5:
        return "warning"
    return "none"


def build_sample_size_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    budget_rows: list[dict[str, object]] = []
    for n_nonmembers in [250, 500, 1000, 2000, 5000]:
        for target_fpr in [0.01, 0.001]:
            expected = n_nonmembers * target_fpr
            budget_rows.append(
                {
                    "n_nonmembers": n_nonmembers,
                    "target_fpr": target_fpr,
                    "expected_false_positives": expected,
                    "warning": warning_label(expected),
                }
            )
    budget = pd.DataFrame(budget_rows)
    budget.to_csv(FINAL_TABLE_DIR / "table5_sample_size_warning_table.csv", index=False)

    budget_md = budget.copy()
    budget_md["n_nonmembers"] = budget_md["n_nonmembers"].map(fmt_count)
    budget_md["target_fpr"] = budget_md["target_fpr"].map(lambda value: FPR_LABELS[float(value)])
    budget_md["expected_false_positives"] = budget_md["expected_false_positives"].map(lambda value: f"{value:g}")
    budget_md = budget_md.rename(
        columns={
            "n_nonmembers": "Non-members",
            "target_fpr": "Target FPR",
            "expected_false_positives": "Expected false positives",
            "warning": "Tail-resolution warning",
        }
    )
    write_markdown_table(
        FINAL_TABLE_DIR / "table5_sample_size_warning_table.md",
        "Table 5. Low-FPR false-positive budgets",
        "Source: finite-sample arithmetic mirrored from `sample_size_requirements.md`; warnings are reporting flags.",
        budget_md,
    )

    required_rows: list[dict[str, object]] = []
    for target_fpr in [0.01, 0.001]:
        for expected_false_positives in [1, 5, 10]:
            required_rows.append(
                {
                    "target_fpr": target_fpr,
                    "expected_false_positives": expected_false_positives,
                    "required_nonmembers": int(expected_false_positives / target_fpr),
                }
            )
    required = pd.DataFrame(required_rows)
    required.to_csv(FINAL_TABLE_DIR / "table5b_minimum_nonmember_requirements.csv", index=False)

    required_md = required.copy()
    required_md["target_fpr"] = required_md["target_fpr"].map(lambda value: FPR_LABELS[float(value)])
    required_md["required_nonmembers"] = required_md["required_nonmembers"].map(fmt_count)
    required_md = required_md.rename(
        columns={
            "target_fpr": "Target FPR",
            "expected_false_positives": "Expected false positives",
            "required_nonmembers": "Required non-members",
        }
    )
    write_markdown_table(
        FINAL_TABLE_DIR / "table5b_minimum_nonmember_requirements.md",
        "Table 5b. Minimum non-member counts for low-FPR reporting",
        "Source: finite-sample arithmetic mirrored from `sample_size_requirements.md`.",
        required_md,
    )
    return budget, required


def copy_appendix_tables() -> pd.DataFrame:
    sources = [
        (
            "A1",
            "Full expanded main metric grid",
            EXPANDED_RESULTS / "metrics" / "main_metrics.csv",
            APPENDIX_TABLE_DIR / "appendix_table_a1_full_main_metrics.csv",
            "Stage1 point metrics for all dataset/model/score/metric rows.",
        ),
        (
            "A2",
            "Full expanded stage1 bootstrap intervals",
            EXPANDED_RESULTS / "metrics" / "confidence_intervals.csv",
            APPENDIX_TABLE_DIR / "appendix_table_a2_stage1_confidence_intervals.csv",
            "Stage1 50-repeat bootstrap intervals for the full grid.",
        ),
        (
            "A3",
            "Selected hardened bootstrap intervals",
            HARDENED_RESULTS / "hardened_confidence_intervals.csv",
            APPENDIX_TABLE_DIR / "appendix_table_a3_hardened_confidence_intervals.csv",
            "Selected main-table 1,000-repeat bootstrap intervals.",
        ),
        (
            "A4",
            "Stage1 versus hardened interval comparison",
            HARDENED_RESULTS / "stage1_vs_hardened_confidence_intervals.csv",
            APPENDIX_TABLE_DIR / "appendix_table_a4_stage1_vs_hardened_ci.csv",
            "Point and CI-width comparison between stage1 and hardened rows.",
        ),
        (
            "A5",
            "Sample-size sensitivity summary",
            EXPANDED_RESULTS / "subsampling" / "sample_size_sensitivity.csv",
            APPENDIX_TABLE_DIR / "appendix_table_a5_sample_size_sensitivity.csv",
            "Repeated balanced audit-subsampling summary over audit sizes.",
        ),
        (
            "A6",
            "Sample-size repeat-level results",
            EXPANDED_RESULTS / "subsampling" / "sample_size_repeats.csv",
            APPENDIX_TABLE_DIR / "appendix_table_a6_sample_size_repeats.csv",
            "Repeat-level subsampling outputs used to summarize sensitivity.",
        ),
        (
            "A7",
            "Sample-size skipped rows",
            EXPANDED_RESULTS / "subsampling" / "sample_size_skipped.csv",
            APPENDIX_TABLE_DIR / "appendix_table_a7_sample_size_skipped.csv",
            "Subsampling combinations skipped because the requested audit size exceeded an available pool.",
        ),
    ]
    manifest_rows: list[dict[str, object]] = []
    for appendix_id, title, source, target, description in sources:
        data = pd.read_csv(source)
        data.to_csv(target, index=False)
        manifest_rows.append(
            {
                "appendix_id": appendix_id,
                "title": title,
                "rows": len(data),
                "columns": len(data.columns),
                "source_file": str(source.relative_to(PROJECT_ROOT)),
                "output_file": str(target.relative_to(PROJECT_ROOT)),
                "description": description,
            }
        )
    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(APPENDIX_TABLE_DIR / "appendix_table_manifest.csv", index=False)

    md = manifest.copy()
    md["rows"] = md["rows"].map(fmt_count)
    md = md.rename(
        columns={
            "appendix_id": "ID",
            "title": "Title",
            "rows": "Rows",
            "columns": "Columns",
            "source_file": "Source file",
            "output_file": "Output file",
            "description": "Description",
        }
    )
    write_markdown_table(
        APPENDIX_TABLE_DIR / "appendix_table_manifest.md",
        "Appendix Table Manifest",
        "Appendix CSVs preserve full-grid and repeat-level outputs. Stage1 intervals use 50 bootstrap repeats unless explicitly labeled hardened.",
        md,
    )
    return manifest


def write_final_manifest(outputs: dict[str, pd.DataFrame]) -> None:
    rows = []
    for name, table in outputs.items():
        rows.append({"table": name, "rows": len(table), "columns": len(table.columns)})
    overview = pd.DataFrame(rows)

    text = "# Final Tables Manifest\n\n"
    text += "Generated from `expanded_tabular_stage1` and `final_ci_hardening`.\n\n"
    text += "## Main Tables\n\n"
    text += "- `table1_dataset_split_summary`: dataset sizes, feature counts, classes, and member/non-member audit pools.\n"
    text += "- `table2_model_comparison`: 25-row descriptive model comparison with train/non-member accuracy, best AUC, and negative-loss low-FPR point metrics.\n"
    text += "- `table3_main_mia_metrics_hardened`: 25-row main MIA table with 1,000-bootstrap hardened intervals for best-AUC and negative-loss low-FPR metrics.\n"
    text += "- `table4_uncertainty_summary`: interval-width summary for selected hardened rows.\n"
    text += "- `table5_sample_size_warning_table` and `table5b_minimum_nonmember_requirements`: finite-sample low-FPR reporting requirements.\n\n"
    text += "## Scope Boundary\n\n"
    text += "Main manuscript tables use selected hardened intervals. Appendix A2 preserves full-grid stage1 intervals with 50 bootstrap repeats; do not describe those rows as hardened unless they are also present in Appendix A3.\n\n"
    text += "## Output Sizes\n\n"
    text += overview.to_markdown(index=False)
    text += "\n"
    (FINAL_TABLE_DIR / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    FINAL_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    APPENDIX_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    summary = load_summary()
    hardened = load_hardened()

    outputs = {
        "table1_dataset_split_summary": build_dataset_table(),
        "table2_model_comparison": build_model_comparison_table(summary),
        "table3_main_mia_metrics_hardened": build_main_mia_table(summary, hardened),
        "table4_uncertainty_summary": build_uncertainty_summary(hardened),
    }
    budget, required = build_sample_size_tables()
    outputs["table5_sample_size_warning_table"] = budget
    outputs["table5b_minimum_nonmember_requirements"] = required
    outputs["appendix_table_manifest"] = copy_appendix_tables()
    write_final_manifest(outputs)

    print(f"Wrote final tables to {FINAL_TABLE_DIR.relative_to(PROJECT_ROOT)}")
    print(f"Wrote appendix tables to {APPENDIX_TABLE_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
