# Final Tables Manifest

Generated from `expanded_tabular_stage1` and `final_ci_hardening`.

## Main Tables

- `table1_dataset_split_summary`: dataset sizes, feature counts, classes, and member/non-member audit pools.
- `table2_model_comparison`: 25-row descriptive model comparison with train/non-member accuracy, best AUC, and negative-loss low-FPR point metrics.
- `table3_main_mia_metrics_hardened`: 25-row main MIA table with 1,000-bootstrap hardened intervals for best-AUC and negative-loss low-FPR metrics.
- `table4_uncertainty_summary`: interval-width summary for selected hardened rows.
- `table5_sample_size_warning_table` and `table5b_minimum_nonmember_requirements`: finite-sample low-FPR reporting requirements.

## Scope Boundary

Main manuscript tables use selected hardened intervals. Appendix A2 preserves full-grid stage1 intervals with 50 bootstrap repeats; do not describe those rows as hardened unless they are also present in Appendix A3.

## Output Sizes

| table                                  |   rows |   columns |
|:---------------------------------------|-------:|----------:|
| table1_dataset_split_summary           |      5 |         8 |
| table2_model_comparison                |     25 |        12 |
| table3_main_mia_metrics_hardened       |     25 |        18 |
| table4_uncertainty_summary             |      3 |        10 |
| table5_sample_size_warning_table       |     10 |         4 |
| table5b_minimum_nonmember_requirements |      6 |         3 |
| appendix_table_manifest                |      7 |         7 |
