# Reusable Audit Tool Run Summary

Generated: 2026-06-05T01:11:37-04:00

## Input

- Input path: `analysis/results/q1_lira_like_appendix/score_arrays/credit_default_random_forest_shadow_lira_like_neg_loss.npz`
- Input format: `npz`
- Dataset label: `credit_default`
- Model label: `random_forest_shadow_lira_like_neg_loss`
- Score names: `['shadow_lira_like_neg_loss']`
- Members / non-members: 15000 / 15000

## Settings

- FPR levels: `[0.01, 0.001]`
- Bootstrap repeats: 1000
- Confidence: 0.95
- Subsampling repeats: 200
- Sample sizes: `[500, 1000, 2500, 5000, 10000, 15000, 20000]`
- Random state: 20260602

## Outputs

- main_metrics: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/metrics/main_metrics.csv`
- confidence_intervals: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/metrics/confidence_intervals.csv`
- fixed_threshold_intervals: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/metrics/fixed_threshold_intervals.csv`
- sample_size_repeats: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/subsampling/sample_size_repeats.csv`
- sample_size_sensitivity: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/subsampling/sample_size_sensitivity.csv`
- sample_size_skipped: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/subsampling/sample_size_skipped.csv`
- tail_resolution_warnings: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/diagnostics/tail_resolution_warnings.csv`
- run_config: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/run_config.json`
- run_summary: `analysis/results/q1_lira_like_appendix/audit_tool/credit_default_random_forest_shadow_lira_like_neg_loss/run_summary.md`

## AUC Snapshot

| Attack Score | AUC |
| --- | ---: |
| shadow_lira_like_neg_loss | 0.6254 |

## Tail-Resolution Warnings

| Attack Score | Context | Target FPR | Expected FPs | Warning |
| --- | --- | ---: | ---: | --- |
| shadow_lira_like_neg_loss | sample_size_500 | 0.001 | 0.500 | severe_tail_resolution_warning |
| shadow_lira_like_neg_loss | sample_size_1000 | 0.001 | 1.000 | tail_resolution_warning |
| shadow_lira_like_neg_loss | sample_size_2500 | 0.001 | 2.500 | tail_resolution_warning |

## Interpretation Notes

- Larger scores are interpreted as more member-like.
- Low-FPR metrics use tie-aware randomized threshold handling.
- Bootstrap intervals resample member and non-member scores separately.
- Fixed-threshold Wilson intervals are conditional on the selected threshold/tie rule.
- Subsampling rows estimate how metrics vary when the balanced audit sample is smaller than the available score pool.
