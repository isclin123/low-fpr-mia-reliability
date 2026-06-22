# Q1 Split/Seed Sensitivity

This bounded check repeats the target member/non-member split and target-model random seed, then recomputes negative-loss member/non-member score arrays and low-FPR metrics.

It is a combined split-plus-seed sensitivity check. It is not a factorial decomposition of split variability versus learner-seed variability, and it is not a new attack benchmark.

## Paper-ready table

| Setting | Repeats | AUC mean [min, max] | TPR@1%FPR mean [min, max] | TPR@0.1%FPR mean [min, max] | Accuracy gap mean [min, max] |
|---|---:|---:|---:|---:|---:|
| CD/RF | 5 | 0.7594 [0.7547, 0.7626] | 0.0578 [0.0487, 0.0638] | 0.0063 [0.0051, 0.0068] | 0.1839 [0.1813, 0.1879] |
| CD/ET | 5 | 0.9977 [0.9974, 0.9980] | 0.9991 [0.9988, 0.9993] | 0.3183 [0.2457, 0.3747] | 0.1896 [0.1873, 0.1938] |
| Adult/RF | 5 | 0.6250 [0.6209, 0.6286] | 0.0141 [0.0137, 0.0144] | 0.0014 [0.0014, 0.0014] | 0.1451 [0.1434, 0.1478] |

## Design

- Split/model seeds: `[20260602, 20260603, 20260604, 20260605, 20260606]`
- Settings: `[{'dataset': 'credit_default', 'model': 'random_forest', 'label': 'CD/RF'}, {'dataset': 'credit_default', 'model': 'extra_trees', 'label': 'CD/ET'}, {'dataset': 'adult_income', 'model': 'random_forest', 'label': 'Adult/RF'}]`
- Scores evaluated: `['neg_loss']`
- Random forest / ExtraTrees estimators: `200`
- Maximum iterations for iterative estimators: `1000`

## Outputs

- Per-seed metric rows: `analysis/results/q1_split_seed_sensitivity/split_seed_metric_rows.csv`
- Metric summaries: `analysis/results/q1_split_seed_sensitivity/split_seed_summary.csv`
- Paper table: `analysis/results/q1_split_seed_sensitivity/paper_table_split_seed_sensitivity.csv`
- Run config: `analysis/results/q1_split_seed_sensitivity/run_config.json`
