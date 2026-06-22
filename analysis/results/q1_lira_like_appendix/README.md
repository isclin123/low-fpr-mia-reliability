# Q1 Bounded LiRA-Like Shadow Score Appendix

Generated: 2026-06-05T01:11:49-04:00

## Scope

This is a bounded score-array compatibility case for the reusable audit workflow. It is not a full LiRA benchmark, not an RMIA benchmark, and not a claim that the implemented score is a state-of-the-art membership attack.

The score is a global shadow-model log-likelihood ratio over target-model `neg_loss`:

`log p(target neg_loss | shadow train scores) - log p(target neg_loss | shadow holdout scores)`

The shadow distributions are Gaussian fits pooled across a small number of random-forest shadow models trained with the same cleaned data representation and target-model family.

## Key Metrics

| Dataset | Score source | Attack score | AUC | TPR@1%FPR | TPR@0.1%FPR | Members | Non-members |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| credit_default | target_base_neg_loss | neg_loss | 0.7584 | 0.0487 | 0.0051 | 15000 | 15000 |
| credit_default | bounded_shadow_lira_like | shadow_lira_like_neg_loss | 0.6254 | 0.0089 | 0.0009 | 15000 | 15000 |
| adult_income | target_base_neg_loss | neg_loss | 0.6286 | 0.0141 | 0.0014 | 24421 | 24421 |
| adult_income | bounded_shadow_lira_like | shadow_lira_like_neg_loss | 0.6178 | 0.0120 | 0.0012 | 24421 | 24421 |

## Shadow Fit Summary

| Dataset | Shadows | Train/holdout per shadow | Shadow train mean/std | Shadow holdout mean/std |
| --- | ---: | ---: | ---: | ---: |
| credit_default | 8 | 5000 / 5000 | -0.1164 / 0.1184 | -0.4650 / 0.9178 |
| adult_income | 8 | 8000 / 8000 | -0.0845 / 0.1137 | -0.3614 / 1.2021 |

## Outputs

- Score arrays: `analysis/results/q1_lira_like_appendix/score_arrays`
- Audit-tool outputs: `analysis/results/q1_lira_like_appendix/audit_tool`
- Summary tables: `analysis/results/q1_lira_like_appendix/tables`
- Run config: `analysis/results/q1_lira_like_appendix/run_config.json`

## Limitations

- This uses global shadow train/holdout score distributions, not per-example in/out shadow distributions as in full LiRA.
- The Gaussian density model is a lightweight compatibility device over `neg_loss`; no RMIA offline/online ratio, population prior, or difficulty calibration is implemented.
- Shadow models are bounded in count and training size for appendix evidence, so the result should be interpreted as an audit-tool compatibility case rather than an attack benchmark.
- Target member and non-member score arrays come from the existing target RF artifacts and existing member/non-member split.
