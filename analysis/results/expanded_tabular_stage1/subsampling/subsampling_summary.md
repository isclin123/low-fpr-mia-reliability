# Sample-Size Sensitivity Summary

Generated: 2026-06-03T11:20:42-04:00

## Configuration

- Datasets: `['credit_default', 'covertype', 'adult_income', 'bank_marketing', 'diabetes_readmission']`
- Models: `['logistic_regression', 'random_forest', 'hist_gradient_boosting', 'extra_trees', 'small_mlp']`
- Attack score source: `expanded_tabular_stage1/attack_scores`
- Sample sizes: `[250, 500, 1000, 2000, 5000]`
- Repeats per sample size: 50

## Outputs

- Repeated subsampling rows: `analysis/results/expanded_tabular_stage1/subsampling/sample_size_repeats.csv`
- Aggregated sensitivity table: `analysis/results/expanded_tabular_stage1/subsampling/sample_size_sensitivity.csv`
- Skipped sample sizes: `analysis/results/expanded_tabular_stage1/subsampling/sample_size_skipped.csv`

## AUC Stability Snapshot

| Dataset | Model | Attack Score | Audit Size | Mean AUC | 95% Width |
| --- | --- | --- | ---: | ---: | ---: |
| adult_income | extra_trees | confidence | 250 | 0.8660 | 0.0451 |
| adult_income | extra_trees | confidence | 500 | 0.8665 | 0.0374 |
| adult_income | extra_trees | confidence | 1000 | 0.8686 | 0.0241 |
| adult_income | extra_trees | confidence | 2000 | 0.8685 | 0.0185 |
| adult_income | extra_trees | confidence | 5000 | 0.8680 | 0.0083 |
| adult_income | extra_trees | modified_entropy | 250 | 0.8680 | 0.0462 |
| adult_income | extra_trees | modified_entropy | 500 | 0.8684 | 0.0392 |
| adult_income | extra_trees | modified_entropy | 1000 | 0.8704 | 0.0241 |
| adult_income | extra_trees | modified_entropy | 2000 | 0.8702 | 0.0180 |
| adult_income | extra_trees | modified_entropy | 5000 | 0.8698 | 0.0080 |
| adult_income | extra_trees | neg_entropy | 250 | 0.8660 | 0.0451 |
| adult_income | extra_trees | neg_entropy | 500 | 0.8665 | 0.0374 |
| adult_income | extra_trees | neg_entropy | 1000 | 0.8686 | 0.0241 |
| adult_income | extra_trees | neg_entropy | 2000 | 0.8685 | 0.0185 |
| adult_income | extra_trees | neg_entropy | 5000 | 0.8680 | 0.0083 |
| adult_income | extra_trees | neg_loss | 250 | 0.8680 | 0.0462 |
| adult_income | extra_trees | neg_loss | 500 | 0.8684 | 0.0392 |
| adult_income | extra_trees | neg_loss | 1000 | 0.8704 | 0.0241 |
| adult_income | extra_trees | neg_loss | 2000 | 0.8702 | 0.0180 |
| adult_income | extra_trees | neg_loss | 5000 | 0.8698 | 0.0080 |
| adult_income | hist_gradient_boosting | confidence | 250 | 0.5089 | 0.0839 |
| adult_income | hist_gradient_boosting | confidence | 500 | 0.5029 | 0.0574 |
| adult_income | hist_gradient_boosting | confidence | 1000 | 0.5045 | 0.0455 |
| adult_income | hist_gradient_boosting | confidence | 2000 | 0.5045 | 0.0358 |
| adult_income | hist_gradient_boosting | confidence | 5000 | 0.5054 | 0.0151 |
| adult_income | hist_gradient_boosting | modified_entropy | 250 | 0.5171 | 0.0913 |
| adult_income | hist_gradient_boosting | modified_entropy | 500 | 0.5096 | 0.0597 |
| adult_income | hist_gradient_boosting | modified_entropy | 1000 | 0.5112 | 0.0428 |
| adult_income | hist_gradient_boosting | modified_entropy | 2000 | 0.5103 | 0.0365 |
| adult_income | hist_gradient_boosting | modified_entropy | 5000 | 0.5114 | 0.0158 |
| adult_income | hist_gradient_boosting | neg_entropy | 250 | 0.5089 | 0.0839 |
| adult_income | hist_gradient_boosting | neg_entropy | 500 | 0.5029 | 0.0574 |
| adult_income | hist_gradient_boosting | neg_entropy | 1000 | 0.5045 | 0.0455 |
| adult_income | hist_gradient_boosting | neg_entropy | 2000 | 0.5045 | 0.0358 |
| adult_income | hist_gradient_boosting | neg_entropy | 5000 | 0.5054 | 0.0151 |
| adult_income | hist_gradient_boosting | neg_loss | 250 | 0.5171 | 0.0913 |
| adult_income | hist_gradient_boosting | neg_loss | 500 | 0.5096 | 0.0597 |
| adult_income | hist_gradient_boosting | neg_loss | 1000 | 0.5112 | 0.0428 |
| adult_income | hist_gradient_boosting | neg_loss | 2000 | 0.5103 | 0.0365 |
| adult_income | hist_gradient_boosting | neg_loss | 5000 | 0.5114 | 0.0158 |

## Notes

- Each repeat samples balanced member and non-member audit subsets without replacement.
- Within each dataset/model/sample-size/repeat, the same sampled rows are reused for every attack score.
- The 95% width is the empirical 97.5th minus 2.5th percentile across repeats.
- Low-FPR metrics use the same tie-aware randomized operating-point convention as the main metric tables.
- Warnings are added when the expected false-positive budget is very small.
