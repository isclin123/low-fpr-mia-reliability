# Data Dictionary: credit_default

Generated: 2026-06-02T14:26:15-04:00

## Summary

- Description: UCI Default of Credit Card Clients financial tabular dataset.
- Task type: `binary_classification`
- Rows: 30000
- Features: 23
- Target: `default payment next month`
- Target classes/counts: `{'0': 23364, '1': 6636}`

## Split

- Random state: `20260602`
- Member/target-train rows: 15000
- Non-member/target-test rows: 15000
- Split rule: 50/50 stratified split; target-train rows are treated as members, held-out target-test rows as non-members.

## Features

| Index | Feature | Stored dtype |
| --- | --- | --- |
| 0 | `LIMIT_BAL` | `float32` |
| 1 | `SEX` | `float32` |
| 2 | `EDUCATION` | `float32` |
| 3 | `MARRIAGE` | `float32` |
| 4 | `AGE` | `float32` |
| 5 | `PAY_0` | `float32` |
| 6 | `PAY_2` | `float32` |
| 7 | `PAY_3` | `float32` |
| 8 | `PAY_4` | `float32` |
| 9 | `PAY_5` | `float32` |
| 10 | `PAY_6` | `float32` |
| 11 | `BILL_AMT1` | `float32` |
| 12 | `BILL_AMT2` | `float32` |
| 13 | `BILL_AMT3` | `float32` |
| 14 | `BILL_AMT4` | `float32` |
| 15 | `BILL_AMT5` | `float32` |
| 16 | `BILL_AMT6` | `float32` |
| 17 | `PAY_AMT1` | `float32` |
| 18 | `PAY_AMT2` | `float32` |
| 19 | `PAY_AMT3` | `float32` |
| 20 | `PAY_AMT4` | `float32` |
| 21 | `PAY_AMT5` | `float32` |
| 22 | `PAY_AMT6` | `float32` |
