# Metric Table Summary

Generated: 2026-06-03T11:20:19-04:00

## Configuration

- Datasets: `['credit_default', 'covertype', 'adult_income', 'bank_marketing', 'diabetes_readmission']`
- Models: `['logistic_regression', 'random_forest', 'hist_gradient_boosting', 'extra_trees', 'small_mlp']`
- Attack score source: `expanded_tabular_stage1/attack_scores`
- Bootstrap repeats: 50
- Confidence: 0.95

## Outputs

- Main metrics: `05_analysis/results/expanded_tabular_stage1/metrics/main_metrics.csv`
- Confidence intervals: `05_analysis/results/expanded_tabular_stage1/metrics/confidence_intervals.csv`

## Highest Smoke/Core AUC Rows

| Dataset | Model | Attack Score | AUC |
| --- | --- | --- | --- |
| diabetes_readmission | extra_trees | neg_loss | 0.9982 |
| diabetes_readmission | extra_trees | modified_entropy | 0.9982 |
| diabetes_readmission | extra_trees | confidence | 0.9982 |
| diabetes_readmission | extra_trees | neg_entropy | 0.9982 |
| credit_default | extra_trees | neg_loss | 0.9977 |
| credit_default | extra_trees | modified_entropy | 0.9977 |
| credit_default | extra_trees | confidence | 0.9971 |
| credit_default | extra_trees | neg_entropy | 0.9971 |
| covertype | extra_trees | neg_loss | 0.9769 |
| covertype | extra_trees | confidence | 0.9769 |

## Notes

- Larger attack scores are interpreted as more member-like.
- Low-FPR thresholds are estimated from non-member score tails.
- Ties at the low-FPR threshold use randomized tie-breaking, so reported TPR/FPR values are expected operating-point values rather than all-ties-included values.
- Bootstrap intervals resample member and non-member scores separately.
