# Final CI Hardening Summary

Generated: 2026-06-03T11:59:10-04:00

## Scope

- Source run: `expanded_tabular_stage1`
- Attack-score subdir: `expanded_tabular_stage1/attack_scores`
- Summary CSV used for row selection: `figures_tables/expanded/expanded_model_comparison_summary.csv`
- Output directory: `analysis/results/final_ci_hardening`
- Datasets: `['adult_income', 'bank_marketing', 'covertype', 'credit_default', 'diabetes_readmission']`
- Models: `['extra_trees', 'hist_gradient_boosting', 'logistic_regression', 'random_forest', 'small_mlp']`
- Selected score rows: `37`
- Hardened CI rows: `111`
- Metrics: `['AUC', 'TPR@0.1%FPR', 'TPR@1%FPR']`

## Bootstrap Settings

- Bootstrap repeats: `1000`
- Confidence level: `0.95`
- Random state base: `20260603`

## Outputs

- Selected score rows: `analysis/results/final_ci_hardening/selected_score_rows.csv`
- Hardened intervals: `analysis/results/final_ci_hardening/hardened_confidence_intervals.csv`
- Stage1 comparison: `analysis/results/final_ci_hardening/stage1_vs_hardened_confidence_intervals.csv`
- Run config: `analysis/results/final_ci_hardening/run_config.json`

## Interpretation Boundary

- This hardening targets main-table candidate rows, not every score/metric in the expanded stage1 grid.
- Selected scores include each dataset/model's best-AUC score and the canonical negative-loss score.
- The hardened rows support final Results v2 wording for AUC and low-FPR TPR intervals.
- AUC intervals use an exact pre-sorted weighted bootstrap implementation to avoid repeated score sorting on large datasets.

## Timings

| Stage | Seconds |
|---|---:|
| select_rows | 0.01 |
| bootstrap_hardening | 186.05 |
