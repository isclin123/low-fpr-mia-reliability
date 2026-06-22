# Q1 Tie-Rule Sensitivity

This sensitivity analysis compares three low-FPR operating rules using the existing expanded Stage1 negative-loss score arrays:

- Strict: scores are positive only when `score > threshold`.
- Inclusive: scores are positive when `score >= threshold`.
- Randomized tie-aware: scores above threshold are positive, and threshold ties are included with the fraction needed to match the target FPR in expectation.

The threshold is the existing Stage1 non-member tail threshold, `np.quantile(nonmember_scores, 1 - target_fpr, method="higher")`.

## Paper-ready table

| Setting | Target FPR | Threshold | Tie frac. | Strict TPR/FPR | Randomized TPR/FPR | Inclusive TPR/FPR |
|---|---:|---:|---:|---:|---:|---:|
| CD/RF | 1% | -0.0100503 | 0.163 | 0.0431/0.0086 | 0.0487/0.0100 | 0.0779/0.0172 |
| CD/RF | 0.1% | 0 | 0.349 | 0.0000/0.0000 | 0.0051/0.0010 | 0.0145/0.0029 |
| CD/ET | 1% | -0.0100503 | 0.744 | 0.9988/0.0055 | 0.9988/0.0100 | 0.9988/0.0115 |
| CD/ET | 0.1% | 0 | 0.366 | 0.0000/0.0000 | 0.3654/0.0010 | 0.9988/0.0027 |
| Diab/RF | 1% | -0.0151136 | 0.070 | 0.1108/0.0094 | 0.1158/0.0100 | 0.1830/0.0183 |
| Diab/RF | 0.1% | 0 | 0.795 | 0.0000/0.0000 | 0.0126/0.0010 | 0.0158/0.0013 |
| Diab/ET | 1% | -0.00501254 | 0.984 | 1.0000/0.0036 | 1.0000/0.0100 | 1.0000/0.0101 |
| Diab/ET | 0.1% | 0 | 0.278 | 0.0000/0.0000 | 0.2780/0.0010 | 1.0000/0.0036 |

## Key readout

- Maximum strict-to-inclusive TPR width: 1.0000 (Diab/ET at 0.1% FPR).
- Maximum strict-to-inclusive FPR width: 0.0089.
- The randomized tie-aware column reproduces the intended low-FPR convention by keeping empirical FPR at the target in expectation.

## Outputs

- Long CSV: `analysis/results/q1_tie_rule_sensitivity/tie_rule_operating_points.csv`
- Paper table CSV: `analysis/results/q1_tie_rule_sensitivity/paper_table_tie_rule_sensitivity.csv`
- Run config: `analysis/results/q1_tie_rule_sensitivity/run_config.json`
