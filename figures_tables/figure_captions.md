# Figure Captions

Sources:

- Diagnostic figures were generated from `analysis/generate_figures.py` using the `core` and `model_extension_hgb` result folders.
- Expanded manuscript-facing figures were generated from `analysis/generate_expanded_outputs.py` using `analysis/results/expanded_tabular_stage1/` and the compact summary outputs under `figures_tables/expanded/`.

## Expanded Manuscript-Facing Figures

**expanded_best_auc_heatmap.png**: Best simple-score membership-inference AUC for each dataset and target-model family, selecting the strongest of the four evaluated attack scores per cell. The figure is a descriptive overview of model-family dependence in the expanded five-dataset by five-model grid. It should be read together with Table 2 and Table 3 rather than as a formal ranking or pairwise significance result.

**expanded_neg_loss_low_fpr_heatmaps.png**: Negative-loss low-FPR operating behavior across datasets and target-model families, shown as side-by-side heatmaps for TPR@1%FPR and TPR@0.1%FPR. The figure highlights that elevated AUC does not uniquely determine low-FPR operating performance and that the same model family can look very different at 1% and 0.1% FPR. The two panels use panel-specific color scales because the value ranges differ substantially between 1% FPR and 0.1% FPR. This figure presents point estimates only; any uncertainty claim should cite Table 3 or the appendix confidence-interval tables rather than relying on the heatmap alone.

**expanded_accuracy_gap_vs_best_auc.png**: Relationship between each target model's train versus non-member accuracy gap and its best observed simple-score MIA AUC in the expanded grid. The figure supports the bounded interpretation that larger train/non-member gaps tend to coincide with stronger simple-score membership signal in this tabular setting, while predictive accuracy alone does not explain the pattern. Near-random model families cluster near the baseline AUC region, so the figure is best used as a pattern summary rather than a precise visual ranking among weak-signal models.

**expanded_auc_width_by_audit_size.png**: Mean 95% repeated-subsampling interval width for AUC as balanced audit sample size increases. The figure shows that uncertainty narrows as more member and non-member audit records become available, reinforcing the paper's finite-sample reporting argument. It supports audit-planning and uncertainty interpretation, not attack ranking.

## Diagnostic Figures

**model_comparison_best_auc.png**: Best membership-inference AUC for each dataset and target model in the original core-plus-HGB diagnostic comparison, selecting the strongest of the four simple attack scores. The dashed line marks random guessing. Random forest produces the strongest MIA signal in this first-pass diagnostic view, while logistic regression and HistGradientBoosting remain near random.

**target_gap_vs_best_auc.png**: Relationship between the target-model train/non-member accuracy gap and the best MIA AUC in the original diagnostic comparison. The plot supports the interpretation that overfitting, rather than predictive accuracy alone, drives the observed simple-score MIA signal.

**low_fpr_roc_neg_loss.png**: Low-FPR region of ROC curves for the negative-loss attack score. This view emphasizes the operating range most relevant for privacy auditing and shows that non-random AUC does not necessarily imply large TPR at very low FPR.

**low_fpr_tpr_neg_loss.png**: TPR at 1% FPR and 0.1% FPR for the negative-loss attack score. Baseline lines mark the corresponding FPR levels, helping show whether the attack meaningfully exceeds random low-FPR behavior.

**audit_size_tpr_mean_neg_loss.png**: Mean low-FPR TPR under repeated balanced audit subsampling. The figure shows how reported low-FPR performance changes when only a finite number of member and non-member audit records are available.

**audit_size_auc_width_neg_loss.png**: Empirical 95% interval width for AUC under repeated audit subsampling. Interval widths shrink as audit sample size increases, supporting the finite-sample uncertainty argument.

**audit_size_tpr001_width_neg_loss.png**: Empirical 95% interval width for TPR at 0.1% FPR under repeated audit subsampling. The smallest audit sizes are especially fragile because the expected number of false positives is below one.

**score_distribution_credit_default_random_forest_neg_loss.png**: Member and non-member negative-loss score distributions for the credit-default random forest. The x-axis is limited to the central 99% of sampled scores for readability.

## QA Boundaries

- `expanded_neg_loss_low_fpr_heatmaps.png` uses panel-specific color scales. The caption and any manuscript reference to this figure should state that the 1% FPR and 0.1% FPR panels are not directly comparable by raw color alone.
- Uncertainty claims should cite `figures_tables/final_tables/table3_main_mia_metrics_hardened.md` or the appendix CI tables, not the heatmap by itself.
- Appendix full-grid confidence intervals remain stage1 50-bootstrap intervals unless separately hardened. Do not describe the full appendix CI grid as hardened solely because the main text uses Table 3.

## File Locations

- `figures_tables/expanded/expanded_accuracy_gap_vs_best_auc.png`
- `figures_tables/expanded/expanded_auc_width_by_audit_size.png`
- `figures_tables/expanded/expanded_best_auc_heatmap.png`
- `figures_tables/expanded/expanded_neg_loss_low_fpr_heatmaps.png`
- `figures_tables/diagnostics/audit_size_auc_width_neg_loss.png`
- `figures_tables/diagnostics/audit_size_tpr001_width_neg_loss.png`
- `figures_tables/diagnostics/audit_size_tpr_mean_neg_loss.png`
- `figures_tables/diagnostics/low_fpr_roc_neg_loss.png`
- `figures_tables/diagnostics/low_fpr_tpr_neg_loss.png`
- `figures_tables/diagnostics/model_comparison_best_auc.png`
- `figures_tables/diagnostics/score_distribution_credit_default_random_forest_neg_loss.png`
- `figures_tables/diagnostics/target_gap_vs_best_auc.png`
