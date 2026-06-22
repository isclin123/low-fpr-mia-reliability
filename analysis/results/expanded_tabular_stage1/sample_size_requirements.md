# Expanded Stage1 Low-FPR Sample-Size Requirements

This note records why low-FPR audit claims require large non-member audit pools.

## Dataset Audit Pools

| dataset              |   n_members |   n_nonmembers |
|:---------------------|------------:|---------------:|
| Credit Default       |       15000 |          15000 |
| Covertype            |      290506 |         290506 |
| Adult Income         |       24421 |          24421 |
| Bank Marketing       |       20594 |          20594 |
| Diabetes Readmission |       50883 |          50883 |

## Expected False-Positive Budgets

|   n_nonmembers |   target_fpr |   expected_false_positives | warning   |
|---------------:|-------------:|---------------------------:|:----------|
|            250 |        0.01  |                       2.5  | warning   |
|            250 |        0.001 |                       0.25 | severe    |
|            500 |        0.01  |                       5    |           |
|            500 |        0.001 |                       0.5  | severe    |
|           1000 |        0.01  |                      10    |           |
|           1000 |        0.001 |                       1    | warning   |
|           2000 |        0.01  |                      20    |           |
|           2000 |        0.001 |                       2    | warning   |
|           5000 |        0.01  |                      50    |           |
|           5000 |        0.001 |                       5    |           |

## Minimum Non-Member Counts

|   target_fpr |   expected_false_positives |   required_nonmembers |
|-------------:|---------------------------:|----------------------:|
|        0.01  |                          1 |                   100 |
|        0.01  |                          5 |                   500 |
|        0.01  |                         10 |                  1000 |
|        0.001 |                          1 |                  1000 |
|        0.001 |                          5 |                  5000 |
|        0.001 |                         10 |                 10000 |

## Interpretation

- At 1% FPR, 500 non-members gives only 5 expected false positives.
- At 0.1% FPR, even 5000 non-members gives only 5 expected false positives.
- Audit sizes below these thresholds can still be reported, but they should carry tail-resolution warnings.
- These constraints are statistical, not implementation bugs.
