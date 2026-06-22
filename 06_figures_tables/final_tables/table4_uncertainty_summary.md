# Table 4. Hardened interval-width summary

Source: selected main-table rows in `final_ci_hardening`; this table summarizes uncertainty, not model superiority.

| Metric      |   Rows |   Median CI width |   75th pct. CI width |   Max CI width | Widest row dataset   | Widest row model    | Widest row score   | Score role                        |   Bootstrap repeats |
|:------------|-------:|------------------:|---------------------:|---------------:|:---------------------|:--------------------|:-------------------|:----------------------------------|--------------------:|
| AUC         |     37 |            0.0075 |               0.0109 |         0.0144 | Credit Default       | Logistic regression | Negative loss      | best_auc_score;canonical_neg_loss |                1000 |
| TPR@0.1%FPR |     37 |            0.001  |               0.0015 |         0.2392 | Credit Default       | ExtraTrees          | Negative loss      | best_auc_score;canonical_neg_loss |                1000 |
| TPR@1%FPR   |     37 |            0.003  |               0.0046 |         0.0151 | Diabetes Readmission | Random Forest       | Negative loss      | canonical_neg_loss                |                1000 |
