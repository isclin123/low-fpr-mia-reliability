# Q1 audit-label uncertainty stress test

Date: 2026-06-04

Status: completed bounded realism/robustness supplement.

## Purpose

This folder records the Q1 minimal realism supplement. It asks whether the score-array reporting workflow still gives useful warnings and bounds when audit membership labels are slightly uncertain.

This is not a production-audit simulation and not a new benchmark. It is a one-setting stress test on:

- Dataset: `credit_default`
- Target model: `random_forest`
- Attack score: `neg_loss`
- Source score arrays: `analysis/results/expanded_tabular_stage1/attack_scores/credit_default/random_forest/attack_scores.npz`

## Stress design

The test simulates audit-label uncertainty by symmetrically swapping a small fraction of member and non-member audit labels. For example, 1% corruption swaps 150 member scores into the observed non-member pool and 150 non-member scores into the observed member pool. This keeps the observed audit sizes fixed at 15,000 members and 15,000 non-members while degrading the reliability of the membership labels used for evaluation.

Corruption rates:

- 0%
- 0.5%
- 1%
- 2%
- 5%

For each rate, the script computes 200 repeated corruption draws and also saves one canonical corrupted score array for audit-tool processing.

## Commands

Generate repeated stress summaries and canonical corrupted arrays:

```bash
python3 analysis/run_q1_label_uncertainty_stress.py
```

Audit each canonical corrupted score array:

```bash
python3 analysis/run_audit_tool.py \
  --input analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/score_arrays/neg_loss_label_corruption_0p000.npz \
  --input-format npz \
  --output-dir analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_0p000 \
  --dataset credit_default \
  --model random_forest_neg_loss_label_corruption_0p000 \
  --score-names neg_loss \
  --n-bootstrap 1000 \
  --n-repeats 200 \
  --sample-sizes 250 500 1000 2500 5000 10000 \
  --skip-figures
```

The same command was repeated for rate slugs `0p005`, `0p010`, `0p020`, and `0p050`.

## Outputs

- Script: `analysis/run_q1_label_uncertainty_stress.py`
- Run config: `run_config.json`
- Canonical corrupted score arrays: `score_arrays/`
- Repeated corruption rows: `tables/label_uncertainty_repeats.csv`
- Repeated corruption summary: `tables/label_uncertainty_summary.csv`
- Canonical point metrics: `tables/canonical_corruption_metrics.csv`
- Canonical score-array manifest: `tables/canonical_score_arrays.csv`
- Deterministic tail-budget warnings: `tables/tail_resolution_warnings.csv`
- Audit-tool outputs for canonical arrays: `audit_tool/corruption_*/`

## Repeated stress-test summary

| Corruption rate | AUC mean | TPR@1%FPR mean | TPR@0.1%FPR mean | Membership advantage@1%FPR mean |
|---:|---:|---:|---:|---:|
| 0% | 0.7584 | 0.0487 | 0.0051 | 0.0387 |
| 0.5% | 0.7558 | 0.0478 | 0.0050 | 0.0378 |
| 1% | 0.7532 | 0.0468 | 0.0048 | 0.0368 |
| 2% | 0.7481 | 0.0452 | 0.0047 | 0.0352 |
| 5% | 0.7326 | 0.0401 | 0.0041 | 0.0301 |

The metrics degrade monotonically in expectation as label uncertainty increases, but the central reporting pattern remains: low-FPR TPR is small, and 0.1%FPR interpretation depends strongly on the finite non-member budget.

## Canonical audit-tool intervals

| Corruption rate | Metric | Point | 95% CI |
|---:|---|---:|---|
| 0% | AUC | 0.7584 | [0.7532, 0.7638] |
| 0% | TPR@1%FPR | 0.0487 | [0.0422, 0.0551] |
| 0% | TPR@0.1%FPR | 0.0051 | [0.0038, 0.0074] |
| 5% | AUC | 0.7332 | [0.7273, 0.7385] |
| 5% | TPR@1%FPR | 0.0372 | [0.0316, 0.0442] |
| 5% | TPR@0.1%FPR | 0.0037 | [0.0028, 0.0050] |

## Tail-budget observations

Tail-budget warnings are deterministic for a requested FPR and non-member sample size, so label corruption does not remove them. Across the five corruption rates and seven sample sizes, the warning table contains:

- 15 `tail_resolution_warning` rows.
- 10 `severe_tail_resolution_warning` rows.

At 0.1%FPR, sample sizes 250 and 500 have fewer than one expected false positive; sample sizes 1000 and 2500 have fewer than five expected false positives. These warnings remain useful even when the score signal is perturbed by audit-label uncertainty.

## Manuscript-facing conclusion

This supplement supports a narrow realism claim: under small symmetric audit-label corruption, the point estimates degrade but the reporting workflow still exposes interval bounds and tail-resolution limits. It does not establish production audit readiness because it does not model unknown priors, population mismatch, correlated records, adversarial label errors, or restricted target-model access.
