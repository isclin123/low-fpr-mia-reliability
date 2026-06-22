# Reusable Audit Tool Run Summary

Generated: 2026-06-03T23:09:22-04:00

## Input

- Input path: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/score_arrays/neg_loss_label_corruption_0p050.npz`
- Input format: `npz`
- Dataset label: `credit_default`
- Model label: `random_forest_neg_loss_label_corruption_0p050`
- Score names: `['neg_loss']`
- Members / non-members: 15000 / 15000

## Settings

- FPR levels: `[0.01, 0.001]`
- Bootstrap repeats: 1000
- Confidence: 0.95
- Subsampling repeats: 200
- Sample sizes: `[250, 500, 1000, 2500, 5000, 10000]`
- Random state: 20260602

## Outputs

- main_metrics: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/metrics/main_metrics.csv`
- confidence_intervals: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/metrics/confidence_intervals.csv`
- fixed_threshold_intervals: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/metrics/fixed_threshold_intervals.csv`
- sample_size_repeats: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/subsampling/sample_size_repeats.csv`
- sample_size_sensitivity: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/subsampling/sample_size_sensitivity.csv`
- sample_size_skipped: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/subsampling/sample_size_skipped.csv`
- tail_resolution_warnings: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/diagnostics/tail_resolution_warnings.csv`
- run_config: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/run_config.json`
- run_summary: `/Users/jason/Desktop/MIA/05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p050/run_summary.md`

## AUC Snapshot

| Attack Score | AUC |
| --- | ---: |
| neg_loss | 0.7332 |

## Tail-Resolution Warnings

| Attack Score | Context | Target FPR | Expected FPs | Warning |
| --- | --- | ---: | ---: | --- |
| neg_loss | sample_size_250 | 0.01 | 2.500 | tail_resolution_warning |
| neg_loss | sample_size_250 | 0.001 | 0.250 | severe_tail_resolution_warning |
| neg_loss | sample_size_500 | 0.001 | 0.500 | severe_tail_resolution_warning |
| neg_loss | sample_size_1000 | 0.001 | 1.000 | tail_resolution_warning |
| neg_loss | sample_size_2500 | 0.001 | 2.500 | tail_resolution_warning |

## Interpretation Notes

- Larger scores are interpreted as more member-like.
- Low-FPR metrics use tie-aware randomized threshold handling.
- Bootstrap intervals resample member and non-member scores separately.
- Fixed-threshold Wilson intervals are conditional on the selected threshold/tie rule.
- Subsampling rows estimate how metrics vary when the balanced audit sample is smaller than the available score pool.
