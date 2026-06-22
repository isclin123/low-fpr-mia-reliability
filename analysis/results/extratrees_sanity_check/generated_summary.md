# ExtraTrees Sanity-Check Generated Summary

Generated: 2026-06-03T15:29:26-04:00

## Best ExtraTrees Score per Dataset

| dataset              | attack_score     |      auc |   tpr_at_1pct_fpr |   tpr_at_0_1pct_fpr |
|:---------------------|:-----------------|---------:|------------------:|--------------------:|
| adult_income         | modified_entropy | 0.869666 |          0.038377 |            0.003838 |
| bank_marketing       | modified_entropy | 0.880684 |          0.043701 |            0.004370 |
| covertype            | confidence       | 0.976877 |          0.216231 |            0.021623 |
| credit_default       | modified_entropy | 0.997663 |          0.998800 |            0.365415 |
| diabetes_readmission | modified_entropy | 0.998202 |          1.000000 |            0.278049 |

## Train versus Nonmember Gap

| dataset              |   train_accuracy |   nonmember_accuracy |   accuracy_gap_train_minus_nonmember |   train_log_loss |   nonmember_log_loss |   log_loss_gap_nonmember_minus_train |
|:---------------------|-----------------:|---------------------:|-------------------------------------:|-----------------:|---------------------:|-------------------------------------:|
| credit_default       |         0.999400 |             0.809733 |                             0.189667 |         0.000832 |             0.478629 |                             0.477797 |
| covertype            |         1.000000 |             0.944118 |                             0.055882 |         0.000000 |             0.204254 |                             0.204254 |
| adult_income         |         0.999959 |             0.829941 |                             0.170018 |         0.000057 |             0.489167 |                             0.489110 |
| bank_marketing       |         0.996455 |             0.882976 |                             0.113480 |         0.005143 |             0.772135 |                             0.766992 |
| diabetes_readmission |         1.000000 |             0.888568 |                             0.111432 |         0.000000 |             0.339311 |                             0.339311 |

## Cross-Score Consistency

| dataset              |   scores_with_auc_ge_0_9 |
|:---------------------|-------------------------:|
| adult_income         |                        0 |
| bank_marketing       |                        0 |
| covertype            |                        4 |
| credit_default       |                        4 |
| diabetes_readmission |                        4 |

## Duplicate / Split Checks

| dataset              |   member_nonmember_index_overlap |   all_duplicate_row_fraction |   cross_split_unique_feature_overlap |   member_rows_with_feature_duplicate_in_nonmember |   nonmember_rows_with_feature_duplicate_in_member |   id_like_feature_count | id_like_features   |
|:---------------------|---------------------------------:|-----------------------------:|-------------------------------------:|--------------------------------------------------:|--------------------------------------------------:|------------------------:|:-------------------|
| credit_default       |                                0 |                     0.001867 |                                   20 |                                                21 |                                                22 |                       0 |                    |
| covertype            |                                0 |                     0.000000 |                                    0 |                                                 0 |                                                 0 |                       0 |                    |
| adult_income         |                                0 |                     0.001167 |                                   25 |                                                26 |                                                26 |                       0 |                    |
| bank_marketing       |                                0 |                     0.049068 |                                  897 |                                              1030 |                                              1019 |                       0 |                    |
| diabetes_readmission |                                0 |                     0.000000 |                                    0 |                                                 0 |                                                 0 |                       0 |                    |
