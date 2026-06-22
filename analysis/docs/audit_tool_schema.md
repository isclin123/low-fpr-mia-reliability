# Audit Tool Input and Output Schema

Date: 2026-06-03

Status: implemented for `analysis/run_audit_tool.py`.

## Inputs

The audit tool accepts score arrays where larger values mean more member-like.

### NPZ

Required keys:

| Key pattern | Meaning |
|---|---|
| `member_<score_name>` | One-dimensional scores for member records. |
| `nonmember_<score_name>` | One-dimensional scores for non-member records. |

Example score names:

- `neg_loss`
- `confidence`
- `neg_entropy`
- `modified_entropy`

### CSV

Required columns:

| Column | Meaning |
|---|---|
| `membership` | `1` for member and `0` for non-member. Text values such as `member` and `nonmember` are also accepted. |
| score columns | One or more numeric score columns where larger means more member-like. |

Recommended optional columns:

| Column | Meaning |
|---|---|
| `sample_id` | Stable row identifier. |
| `dataset` | Dataset label. |
| `model` | Target-model label. |

## Main Outputs

| Path | Contents |
|---|---|
| `run_config.json` | Full run configuration, resolved input metadata, output paths, and figure paths. |
| `run_summary.md` | Human-readable summary with input settings, AUC snapshot, warnings, and interpretation notes. |
| `metrics/main_metrics.csv` | AUC, TPR at each requested FPR, membership advantage, thresholds, empirical FPR, and tie fractions. |
| `metrics/confidence_intervals.csv` | Stratified bootstrap intervals for AUC, TPR@FPR, and membership advantage@FPR. |
| `metrics/fixed_threshold_intervals.csv` | Wilson intervals for TPR and membership advantage conditional on the selected threshold/tie rule. |
| `subsampling/sample_size_repeats.csv` | Per-repeat metrics for balanced member/non-member audit subsamples. |
| `subsampling/sample_size_sensitivity.csv` | Empirical mean, quantiles, width, min/max, and instability notes across subsampling repeats. |
| `subsampling/sample_size_skipped.csv` | Requested sample sizes that exceed the available balanced score pool. |
| `diagnostics/tail_resolution_warnings.csv` | Expected false-positive budget and warning level for each FPR/context. |
| `figures/` | Low-FPR ROC, score distributions, TPR-vs-audit-size, and interval-width-vs-audit-size figures. |

## Interpretation Notes

- Bootstrap intervals resample member and non-member score pools separately.
- Fixed-threshold Wilson intervals condition on the threshold selected from the non-member audit scores; they do not include threshold-selection uncertainty.
- Tail-resolution warnings are triggered when `n_nonmembers * target_fpr < 5`, with a severe warning below 1 expected false positive.
- Repeated subsampling reuses the same sampled member/non-member rows across score columns within each repeat, making score comparisons paired within a run.
