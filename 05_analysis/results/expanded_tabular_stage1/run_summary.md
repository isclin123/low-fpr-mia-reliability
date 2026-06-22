# Experiment Run Summary

Generated: 2026-06-03T11:20:42-04:00

## Run

- Run name: `expanded_tabular_stage1`
- Datasets: `['credit_default', 'covertype', 'adult_income', 'bank_marketing', 'diabetes_readmission']`
- Models: `['logistic_regression', 'random_forest', 'hist_gradient_boosting', 'extra_trees', 'small_mlp']`
- Prepare data: `False`
- Model subdir: `expanded_tabular_stage1/models`
- Attack-score subdir: `expanded_tabular_stage1/attack_scores`
- Metrics dir: `05_analysis/results/expanded_tabular_stage1/metrics`
- Subsampling dir: `05_analysis/results/expanded_tabular_stage1/subsampling`

## Key Settings

- Random state: `20260602`
- Max train samples: `None`
- Random forest estimators: `200`
- Bootstrap repeats: `50`
- Subsampling repeats: `50`
- Sample sizes: `[250, 500, 1000, 2000, 5000]`

## Stage Timings

| Stage | Seconds |
| --- | ---: |
| extract_attack_scores | 38.14 |
| metric_tables | 167.31 |
| subsampling | 23.72 |

## Outputs

- Metric table: `05_analysis/results/expanded_tabular_stage1/metrics/main_metrics.csv`
- Confidence intervals: `05_analysis/results/expanded_tabular_stage1/metrics/confidence_intervals.csv`
- Sample-size sensitivity: `05_analysis/results/expanded_tabular_stage1/subsampling/sample_size_sensitivity.csv`
- Per-repeat subsampling records: `05_analysis/results/expanded_tabular_stage1/subsampling/sample_size_repeats.csv`

## Notes

- This runner orchestrates existing modules; it does not change raw data.
- Low-FPR metrics use tie-aware randomized threshold handling.
- Subsampling reuses the same sampled rows across attack scores within each dataset/model/sample-size/repeat.
