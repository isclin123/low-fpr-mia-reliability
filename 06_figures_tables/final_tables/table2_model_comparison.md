# Table 2. Model comparison and point-estimate MIA signal

Source: `06_figures_tables/expanded/expanded_model_comparison_summary.csv`; point estimates are descriptive.

| Dataset              | Model                | Members   | Non-members   |   Features |   Train acc. |   Non-member acc. |   Acc. gap |   Best AUC | Best-AUC score   |   Neg-loss TPR@1%FPR |   Neg-loss TPR@0.1%FPR |
|:---------------------|:---------------------|:----------|:--------------|-----------:|-------------:|------------------:|-----------:|-----------:|:-----------------|---------------------:|-----------------------:|
| Credit Default       | Logistic regression  | 15,000    | 15,000        |         23 |       0.8101 |            0.8105 |    -0.0004 |     0.4967 | Negative loss    |               0.0088 |                 0.0005 |
| Credit Default       | HistGradientBoosting | 15,000    | 15,000        |         23 |       0.8322 |            0.8221 |     0.0101 |     0.5165 | Negative loss    |               0.0096 |                 0.0011 |
| Credit Default       | Random Forest        | 15,000    | 15,000        |         23 |       0.9994 |            0.8145 |     0.1849 |     0.7584 | Modified entropy |               0.0487 |                 0.0051 |
| Credit Default       | ExtraTrees           | 15,000    | 15,000        |         23 |       0.9994 |            0.8097 |     0.1897 |     0.9977 | Negative loss    |               0.9988 |                 0.3654 |
| Credit Default       | Small MLP            | 15,000    | 15,000        |         23 |       0.8213 |            0.8184 |     0.0029 |     0.5033 | Modified entropy |               0.0101 |                 0.0006 |
| Covertype            | Logistic regression  | 290,506   | 290,506       |         54 |       0.7244 |            0.7244 |     0      |     0.5007 | Negative entropy |               0.0098 |                 0.001  |
| Covertype            | HistGradientBoosting | 290,506   | 290,506       |         54 |       0.8431 |            0.8334 |     0.0097 |     0.5068 | Modified entropy |               0.0104 |                 0.001  |
| Covertype            | Random Forest        | 290,506   | 290,506       |         54 |       1      |            0.9449 |     0.0551 |     0.6996 | Negative entropy |               0.0315 |                 0.0031 |
| Covertype            | ExtraTrees           | 290,506   | 290,506       |         54 |       1      |            0.9441 |     0.0559 |     0.9769 | Confidence       |               0.2162 |                 0.0216 |
| Covertype            | Small MLP            | 290,506   | 290,506       |         54 |       0.8415 |            0.8372 |     0.0043 |     0.5026 | Negative loss    |               0.0107 |                 0.0011 |
| Adult Income         | Logistic regression  | 24,421    | 24,421        |        108 |       0.8557 |            0.8494 |     0.0063 |     0.5045 | Negative loss    |               0.0098 |                 0.0014 |
| Adult Income         | HistGradientBoosting | 24,421    | 24,421        |        108 |       0.8907 |            0.8709 |     0.0198 |     0.5117 | Modified entropy |               0.0097 |                 0.0007 |
| Adult Income         | Random Forest        | 24,421    | 24,421        |        108 |       1      |            0.8522 |     0.1478 |     0.6286 | Modified entropy |               0.0141 |                 0.0014 |
| Adult Income         | ExtraTrees           | 24,421    | 24,421        |        108 |       1      |            0.8299 |     0.17   |     0.8697 | Negative loss    |               0.0384 |                 0.0038 |
| Adult Income         | Small MLP            | 24,421    | 24,421        |        108 |       0.8761 |            0.8496 |     0.0266 |     0.513  | Negative loss    |               0.0099 |                 0.0011 |
| Bank Marketing       | Logistic regression  | 20,594    | 20,594        |         62 |       0.9009 |            0.9001 |     0.0008 |     0.5021 | Negative loss    |               0.0102 |                 0.0014 |
| Bank Marketing       | HistGradientBoosting | 20,594    | 20,594        |         62 |       0.9126 |            0.8994 |     0.0133 |     0.5122 | Modified entropy |               0.0121 |                 0.0014 |
| Bank Marketing       | Random Forest        | 20,594    | 20,594        |         62 |       0.9965 |            0.8957 |     0.1008 |     0.6597 | Negative loss    |               0.025  |                 0.0025 |
| Bank Marketing       | ExtraTrees           | 20,594    | 20,594        |         62 |       0.9965 |            0.883  |     0.1135 |     0.8807 | Negative loss    |               0.0437 |                 0.0044 |
| Bank Marketing       | Small MLP            | 20,594    | 20,594        |         62 |       0.9058 |            0.8979 |     0.008  |     0.5071 | Modified entropy |               0.0116 |                 0.0011 |
| Diabetes Readmission | Logistic regression  | 50,883    | 50,883        |        565 |       0.8885 |            0.8881 |     0.0005 |     0.5038 | Negative loss    |               0.0106 |                 0.001  |
| Diabetes Readmission | HistGradientBoosting | 50,883    | 50,883        |        565 |       0.8902 |            0.8888 |     0.0015 |     0.5069 | Negative loss    |               0.0097 |                 0.0012 |
| Diabetes Readmission | Random Forest        | 50,883    | 50,883        |        565 |       1      |            0.8884 |     0.1116 |     0.799  | Modified entropy |               0.1158 |                 0.0126 |
| Diabetes Readmission | ExtraTrees           | 50,883    | 50,883        |        565 |       1      |            0.8886 |     0.1114 |     0.9982 | Negative loss    |               1      |                 0.278  |
| Diabetes Readmission | Small MLP            | 50,883    | 50,883        |        565 |       0.8901 |            0.8875 |     0.0026 |     0.5103 | Modified entropy |               0.0113 |                 0.0017 |
