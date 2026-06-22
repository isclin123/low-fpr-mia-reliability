# Reusable Audit Tool Interface

Date drafted: 2026-06-02

Implementation status: implemented on 2026-06-03 in `analysis/src/mia_eval/audit_tool.py` and `analysis/run_audit_tool.py`.

## Purpose

The reusable audit tool is the paper-facing evaluation artifact. It should take member and non-member membership-inference attack score arrays as input and produce statistically disciplined MIA audit outputs.

The tool should be independent of target-model training. Any model or dataset can use the tool if it can provide member and non-member score arrays where larger scores mean "more likely member."

## Minimum Inputs

The tool should support two input formats.

### Format A: NPZ Score Arrays

Required keys:

- `member_<score_name>`
- `nonmember_<score_name>`

Example keys:

- `member_neg_loss`
- `nonmember_neg_loss`
- `member_confidence`
- `nonmember_confidence`
- `member_neg_entropy`
- `nonmember_neg_entropy`

Optional keys:

- `member_labels`
- `nonmember_labels`
- `member_ids`
- `nonmember_ids`

### Format B: CSV Long Table

Required columns:

| Column | Meaning |
|---|---|
| `sample_id` | stable row/sample identifier |
| `membership` | `1` for member, `0` for non-member |
| one or more score columns | score values where larger means more member-like |

Recommended optional columns:

| Column | Meaning |
|---|---|
| `dataset` | dataset name |
| `model` | target model name |
| `label` | true class label |
| `split` | train/test/calibration/evaluation split label |

Example score columns:

- `neg_loss`
- `confidence`
- `neg_entropy`
- `modified_entropy`

## Command-Line Shape

Target command:

```bash
python analysis/run_audit_tool.py \
  --input analysis/examples/example_scores.npz \
  --input-format npz \
  --output-dir analysis/results/audit_tool_example \
  --score-names neg_loss confidence neg_entropy modified_entropy \
  --fpr-levels 0.01 0.001 \
  --n-bootstrap 1000 \
  --n-repeats 200 \
  --sample-sizes 250 500 1000 2000 5000 \
  --random-state 20260602
```

CSV target command:

```bash
python analysis/run_audit_tool.py \
  --input analysis/examples/example_scores.csv \
  --input-format csv \
  --membership-column membership \
  --score-names neg_loss confidence neg_entropy \
  --output-dir analysis/results/audit_tool_csv_example
```

## Python API Shape

Target API:

```python
from pathlib import Path

from mia_eval.audit_tool import AuditToolConfig, run_audit

config = AuditToolConfig(
    input_path=Path("scores.npz"),
    input_format="npz",
    output_dir=Path("audit_results"),
    score_names=("neg_loss", "confidence", "neg_entropy"),
    fpr_levels=(0.01, 0.001),
    n_bootstrap=1000,
    n_repeats=200,
    sample_sizes=(250, 500, 1000, 2000, 5000),
    random_state=20260602,
)

run_audit(config)
```

## Required Outputs

The tool should create:

| Output | Purpose |
|---|---|
| `run_config.json` | full configuration and random seeds |
| `run_summary.md` | human-readable summary |
| `metrics/main_metrics.csv` | AUC and low-FPR point estimates |
| `metrics/confidence_intervals.csv` | bootstrap confidence intervals |
| `metrics/fixed_threshold_intervals.csv` | binomial/Wilson intervals after selected threshold |
| `subsampling/sample_size_sensitivity.csv` | repeated audit-subsampling summary |
| `subsampling/sample_size_repeats.csv` | per-repeat records |
| `diagnostics/tail_resolution_warnings.csv` | warnings for low expected false-positive budget |
| `figures/` | report-ready diagnostic figures |

Optional outputs:

- `metrics/paired_comparisons.csv`
- `calibration/` outputs if calibration is explicitly enabled later.

## Required Metrics

For each score:

- AUC
- TPR@1%FPR
- TPR@0.1%FPR
- membership advantage at 1% FPR
- membership advantage at 0.1% FPR

## Required Interval Methods

For final paper usage:

- stratified bootstrap CIs;
- repeated subsampling empirical intervals;
- fixed-threshold binomial/Wilson intervals for TPR after threshold selection.

Important interpretation note:

The fixed-threshold binomial/Wilson interval treats the selected threshold as fixed. It is useful as a conditional check, but bootstrap remains important because threshold selection itself is random when non-member audit samples are finite.

## Tail-Resolution Warnings

The tool should flag low-FPR operating points where the non-member audit sample is too small.

Suggested warning levels:

| Condition | Warning |
|---|---|
| `n_nonmember * fpr < 1` | severe tail-resolution warning |
| `1 <= n_nonmember * fpr < 5` | tail-resolution warning |
| `n_nonmember * fpr >= 5` | no automatic warning |

These warnings are part of the paper's reporting guidance.

## Figure Outputs

Minimum report-ready figures:

- low-FPR ROC curve;
- TPR@FPR vs audit sample size;
- interval width vs audit sample size;
- member/non-member score distributions.

Optional:

- calibration reliability diagrams if calibration is enabled.

## Implementation Notes

The implementation should reuse existing modules where possible:

- `mia_eval.metrics`
- `mia_eval.bootstrap`
- `mia_eval.subsampling`
- `mia_eval.experiments`

New likely modules:

- `mia_eval.audit_tool`
- `mia_eval.intervals` for fixed-threshold binomial/Wilson intervals

The tool should not retrain target models. The existing experiment pipeline can keep producing score arrays, but the audit tool should also work on score arrays produced elsewhere.

## Paper Claim Enabled By This Tool

After implementation and example validation, the paper can claim a reusable audit workflow/tool that evaluates MIA score arrays with:

- point metrics;
- uncertainty intervals;
- audit sample-size sensitivity;
- low-FPR tail-resolution warnings;
- report-ready figures and tables.
