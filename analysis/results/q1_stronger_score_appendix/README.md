# Q1 stronger-score appendix demonstration

Date: 2026-06-04

Status: completed bounded appendix demonstration.

## Purpose

This folder records a Q1 compatibility demonstration showing that the existing score-array audit workflow can evaluate member/non-member score arrays produced by a stronger reference-centered score construction. This is not a LiRA, RMIA, or state-of-the-art attack benchmark.

The demonstration uses:

- Mandatory setting: `credit_default` + `random_forest`.
- Optional second setting: `adult_income` + `random_forest`, added because the mandatory setting was stable and cheap.

No additional settings were run.

## Score construction

For each dataset/model setting, the script reuses the existing target random forest from `analysis/results/expanded_tabular_stage1/models/`. It trains 12 reference random forests with 100 trees each on stratified 50% subsets of the same cleaned dataset. For each audited record, it estimates out-of-reference difficulty from reference models that did not train on that record whenever at least three such references are available; otherwise it falls back to the full reference ensemble mean and records the fallback count.

Exported stronger score arrays:

- `ref_centered_neg_loss`: target log(true-class probability) minus out-of-reference mean log(true-class probability).
- `ref_logit_margin`: target true-class logit minus out-of-reference mean true-class logit.
- `ref_z_logit_margin`: `ref_logit_margin` divided by the out-of-reference true-class logit standard deviation.

These are reference-centered compatibility scores, not formal LiRA/RMIA implementations.

## Commands

Mandatory setting:

```bash
python3 analysis/run_q1_stronger_score_appendix.py
python3 analysis/run_audit_tool.py \
  --input analysis/results/q1_stronger_score_appendix/credit_default_random_forest/score_arrays/stronger_scores.npz \
  --input-format npz \
  --output-dir analysis/results/q1_stronger_score_appendix/credit_default_random_forest/audit_tool \
  --dataset credit_default \
  --model random_forest_reference_centered \
  --score-names ref_centered_neg_loss ref_logit_margin ref_z_logit_margin \
  --n-bootstrap 1000 \
  --n-repeats 200 \
  --sample-sizes 250 500 1000 2500 5000 10000
```

Optional second setting:

```bash
python3 analysis/run_q1_stronger_score_appendix.py \
  --dataset adult_income \
  --model random_forest \
  --output-dir analysis/results/q1_stronger_score_appendix/adult_income_random_forest
python3 analysis/run_audit_tool.py \
  --input analysis/results/q1_stronger_score_appendix/adult_income_random_forest/score_arrays/stronger_scores.npz \
  --input-format npz \
  --output-dir analysis/results/q1_stronger_score_appendix/adult_income_random_forest/audit_tool \
  --dataset adult_income \
  --model random_forest_reference_centered \
  --score-names ref_centered_neg_loss ref_logit_margin ref_z_logit_margin \
  --n-bootstrap 1000 \
  --n-repeats 200 \
  --sample-sizes 250 500 1000 2500 5000 10000
```

## Outputs

Mandatory setting:

- Score arrays: `credit_default_random_forest/score_arrays/stronger_scores.npz`
- Score metadata: `credit_default_random_forest/score_arrays/metadata.json`
- Score summary: `credit_default_random_forest/score_arrays/score_summary.csv`
- Reference diagnostics: `credit_default_random_forest/score_arrays/reference_model_diagnostics.csv`
- Baseline comparison metrics: `credit_default_random_forest/comparison_metrics.csv`
- Audit-tool outputs: `credit_default_random_forest/audit_tool/`

Optional second setting:

- Score arrays: `adult_income_random_forest/score_arrays/stronger_scores.npz`
- Score metadata: `adult_income_random_forest/score_arrays/metadata.json`
- Score summary: `adult_income_random_forest/score_arrays/score_summary.csv`
- Reference diagnostics: `adult_income_random_forest/score_arrays/reference_model_diagnostics.csv`
- Baseline comparison metrics: `adult_income_random_forest/comparison_metrics.csv`
- Audit-tool outputs: `adult_income_random_forest/audit_tool/`

Script:

- `analysis/run_q1_stronger_score_appendix.py`

## Compact results

| Setting | Score source | Score | AUC | TPR@1%FPR | TPR@0.1%FPR |
|---|---|---|---:|---:|---:|
| `credit_default/random_forest` | simple-score baseline | `neg_loss` | 0.7584 | 0.0487 | 0.0051 |
| `credit_default/random_forest` | reference-centered | `ref_logit_margin` | 0.9254 | 0.3307 | 0.0091 |
| `credit_default/random_forest` | reference-centered | `ref_z_logit_margin` | 0.9250 | 0.3739 | 0.0160 |
| `adult_income/random_forest` | simple-score baseline | `neg_loss` | 0.6286 | 0.0141 | 0.0014 |
| `adult_income/random_forest` | reference-centered | `ref_centered_neg_loss` | 0.7510 | 0.0887 | 0.0039 |
| `adult_income/random_forest` | reference-centered | `ref_z_logit_margin` | 0.7816 | 0.1604 | 0.0030 |

Selected audit-tool intervals:

| Setting | Score | Metric | Point | 95% CI |
|---|---|---|---:|---|
| `credit_default/random_forest` | `ref_z_logit_margin` | AUC | 0.9250 | [0.9219, 0.9278] |
| `credit_default/random_forest` | `ref_z_logit_margin` | TPR@1%FPR | 0.3739 | [0.3235, 0.4071] |
| `credit_default/random_forest` | `ref_z_logit_margin` | TPR@0.1%FPR | 0.0160 | [0.0043, 0.0474] |
| `adult_income/random_forest` | `ref_z_logit_margin` | AUC | 0.7816 | [0.7776, 0.7856] |
| `adult_income/random_forest` | `ref_z_logit_margin` | TPR@1%FPR | 0.1604 | [0.1442, 0.1789] |
| `adult_income/random_forest` | `ref_logit_margin` | TPR@0.1%FPR | 0.0080 | [0.0046, 0.0099] |

## Reporting observations

- The audit workflow accepted the stronger score arrays without code changes to the audit layer.
- Both settings show stronger AUC and TPR@1%FPR than the simple negative-loss baseline.
- Low-FPR reporting still needs intervals: for `credit_default/random_forest`, `ref_z_logit_margin` has TPR@0.1%FPR of 0.0160 with a wide 95% interval [0.0043, 0.0474].
- Tail-resolution warnings remain useful for small audit sizes. Each setting's audit output contains 9 `tail_resolution_warning` rows and 6 `severe_tail_resolution_warning` rows across the three scores and the tested sample-size grid.
- The full-input non-member pools have expected false-positive budgets of 15.0 for `credit_default` and 24.421 for `adult_income` at 0.1%FPR; smaller audit samples remain under-resolved.

## Limitations

- This is a compatibility demonstration for reference-centered scores, not a formal LiRA/RMIA implementation.
- The reference ensemble uses 12 models and 100 trees per model; it was chosen for bounded appendix cost, not attack optimality.
- A small fraction of audited records had fewer than three out-of-reference predictions and used the full reference ensemble fallback: 556/30,000 in `credit_default` and 943/48,842 in `adult_income`.
- The results should be used to update the manuscript's stronger-score limitation and appendix note, not to claim a new attack or state-of-the-art performance.
