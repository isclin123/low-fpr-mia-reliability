# Reusable Audit Tool Run Summary

Generated: 2026-06-03T11:06:35-04:00

## Input

- Input path: `/Users/jason/Desktop/MIA/05_analysis/examples/example_scores.npz`
- Input format: `npz`
- Dataset label: `credit_default`
- Model label: `random_forest`
- Score names: `['neg_loss', 'confidence', 'neg_entropy', 'modified_entropy']`
- Members / non-members: 1000 / 1000

## Settings

- FPR levels: `[0.01, 0.001]`
- Bootstrap repeats: 25
- Confidence: 0.95
- Subsampling repeats: 10
- Sample sizes: `[250, 500]`
- Random state: 20260603

## Outputs

- main_metrics: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/metrics/main_metrics.csv`
- confidence_intervals: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/metrics/confidence_intervals.csv`
- fixed_threshold_intervals: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/metrics/fixed_threshold_intervals.csv`
- sample_size_repeats: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/subsampling/sample_size_repeats.csv`
- sample_size_sensitivity: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/subsampling/sample_size_sensitivity.csv`
- sample_size_skipped: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/subsampling/sample_size_skipped.csv`
- tail_resolution_warnings: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/diagnostics/tail_resolution_warnings.csv`
- run_config: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/run_config.json`
- run_summary: `/Users/jason/Desktop/MIA/05_analysis/results/audit_tool_example_npz/run_summary.md`

## AUC Snapshot

| Attack Score | AUC |
| --- | ---: |
| neg_loss | 0.7699 |
| modified_entropy | 0.7699 |
| confidence | 0.7425 |
| neg_entropy | 0.7425 |

## Tail-Resolution Warnings

| Attack Score | Context | Target FPR | Expected FPs | Warning |
| --- | --- | ---: | ---: | --- |
| neg_loss | full_input | 0.001 | 1.000 | tail_resolution_warning |
| neg_loss | sample_size_250 | 0.01 | 2.500 | tail_resolution_warning |
| neg_loss | sample_size_250 | 0.001 | 0.250 | severe_tail_resolution_warning |
| neg_loss | sample_size_500 | 0.001 | 0.500 | severe_tail_resolution_warning |
| confidence | full_input | 0.001 | 1.000 | tail_resolution_warning |
| confidence | sample_size_250 | 0.01 | 2.500 | tail_resolution_warning |
| confidence | sample_size_250 | 0.001 | 0.250 | severe_tail_resolution_warning |
| confidence | sample_size_500 | 0.001 | 0.500 | severe_tail_resolution_warning |
| neg_entropy | full_input | 0.001 | 1.000 | tail_resolution_warning |
| neg_entropy | sample_size_250 | 0.01 | 2.500 | tail_resolution_warning |
| neg_entropy | sample_size_250 | 0.001 | 0.250 | severe_tail_resolution_warning |
| neg_entropy | sample_size_500 | 0.001 | 0.500 | severe_tail_resolution_warning |
| modified_entropy | full_input | 0.001 | 1.000 | tail_resolution_warning |
| modified_entropy | sample_size_250 | 0.01 | 2.500 | tail_resolution_warning |
| modified_entropy | sample_size_250 | 0.001 | 0.250 | severe_tail_resolution_warning |
| modified_entropy | sample_size_500 | 0.001 | 0.500 | severe_tail_resolution_warning |

## Interpretation Notes

- Larger scores are interpreted as more member-like.
- Low-FPR metrics use tie-aware randomized threshold handling.
- Bootstrap intervals resample member and non-member scores separately.
- Fixed-threshold Wilson intervals are conditional on the selected threshold/tie rule.
- Subsampling rows estimate how metrics vary when the balanced audit sample is smaller than the available score pool.
