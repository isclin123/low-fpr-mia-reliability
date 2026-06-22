# Model Comparison Summary

| dataset        | model         |   train_accuracy |   nonmember_accuracy |   accuracy_gap |   best_auc | best_auc_score   |   neg_loss_tpr_at_1pct_fpr |   neg_loss_tpr_at_0_1pct_fpr |
|:---------------|:--------------|-----------------:|---------------------:|---------------:|-----------:|:-----------------|---------------------------:|-----------------------------:|
| Credit Default | Logistic      |           0.8101 |               0.8105 |        -0.0004 |     0.4967 | Negative loss    |                     0.0088 |                       0.0005 |
| Credit Default | HistGB        |           0.8322 |               0.8221 |         0.0101 |     0.5165 | Negative loss    |                     0.0096 |                       0.0011 |
| Credit Default | Random Forest |           0.9994 |               0.8145 |         0.1849 |     0.7584 | Negative loss    |                     0.0487 |                       0.0051 |
| Covertype      | Logistic      |           0.7244 |               0.7244 |         0      |     0.5007 | Negative entropy |                     0.0098 |                       0.001  |
| Covertype      | HistGB        |           0.8431 |               0.8334 |         0.0097 |     0.5068 | Modified entropy |                     0.0104 |                       0.001  |
| Covertype      | Random Forest |           1      |               0.9449 |         0.0551 |     0.6996 | Negative entropy |                     0.0315 |                       0.0031 |
