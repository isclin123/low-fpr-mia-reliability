# Table 3. Main MIA metrics with hardened bootstrap intervals

Source: `final_ci_hardening/hardened_confidence_intervals.csv`; intervals use 1,000 stratified bootstrap repeats.

| Dataset              | Model                | Best-AUC score   | Best AUC, 95% CI        | Neg-loss TPR@1%FPR, 95% CI   | Neg-loss TPR@0.1%FPR, 95% CI   | Members   | Non-members   |
|:---------------------|:---------------------|:-----------------|:------------------------|:-----------------------------|:-------------------------------|:----------|:--------------|
| Credit Default       | Logistic regression  | Negative loss    | 0.4967 [0.4895, 0.5039] | 0.0088 [0.0071, 0.0113]      | 0.0005 [0.0001, 0.0013]        | 15,000    | 15,000        |
| Credit Default       | HistGradientBoosting | Negative loss    | 0.5165 [0.5096, 0.5229] | 0.0096 [0.0073, 0.0122]      | 0.0011 [0.0005, 0.0020]        | 15,000    | 15,000        |
| Credit Default       | Random Forest        | Modified entropy | 0.7584 [0.7530, 0.7639] | 0.0487 [0.0420, 0.0556]      | 0.0051 [0.0037, 0.0075]        | 15,000    | 15,000        |
| Credit Default       | ExtraTrees           | Negative loss    | 0.9977 [0.9970, 0.9983] | 0.9988 [0.9983, 0.9993]      | 0.3654 [0.2774, 0.5167]        | 15,000    | 15,000        |
| Credit Default       | Small MLP            | Modified entropy | 0.5033 [0.4966, 0.5099] | 0.0101 [0.0080, 0.0121]      | 0.0006 [0.0001, 0.0016]        | 15,000    | 15,000        |
| Covertype            | Logistic regression  | Negative entropy | 0.5007 [0.4993, 0.5023] | 0.0098 [0.0094, 0.0103]      | 0.0010 [0.0008, 0.0011]        | 290,506   | 290,506       |
| Covertype            | HistGradientBoosting | Modified entropy | 0.5068 [0.5052, 0.5083] | 0.0104 [0.0098, 0.0110]      | 0.0010 [0.0009, 0.0011]        | 290,506   | 290,506       |
| Covertype            | Random Forest        | Negative entropy | 0.6996 [0.6983, 0.7010] | 0.0315 [0.0308, 0.0323]      | 0.0031 [0.0031, 0.0032]        | 290,506   | 290,506       |
| Covertype            | ExtraTrees           | Confidence       | 0.9769 [0.9765, 0.9772] | 0.2162 [0.2127, 0.2199]      | 0.0216 [0.0213, 0.0220]        | 290,506   | 290,506       |
| Covertype            | Small MLP            | Negative loss    | 0.5026 [0.5010, 0.5040] | 0.0107 [0.0102, 0.0112]      | 0.0011 [0.0010, 0.0013]        | 290,506   | 290,506       |
| Adult Income         | Logistic regression  | Negative loss    | 0.5045 [0.4995, 0.5099] | 0.0098 [0.0080, 0.0111]      | 0.0014 [0.0008, 0.0020]        | 24,421    | 24,421        |
| Adult Income         | HistGradientBoosting | Modified entropy | 0.5117 [0.5067, 0.5166] | 0.0097 [0.0078, 0.0120]      | 0.0007 [0.0003, 0.0013]        | 24,421    | 24,421        |
| Adult Income         | Random Forest        | Modified entropy | 0.6286 [0.6235, 0.6335] | 0.0141 [0.0137, 0.0146]      | 0.0014 [0.0014, 0.0015]        | 24,421    | 24,421        |
| Adult Income         | ExtraTrees           | Negative loss    | 0.8697 [0.8670, 0.8723] | 0.0384 [0.0376, 0.0391]      | 0.0038 [0.0038, 0.0039]        | 24,421    | 24,421        |
| Adult Income         | Small MLP            | Negative loss    | 0.5130 [0.5078, 0.5183] | 0.0099 [0.0083, 0.0115]      | 0.0011 [0.0009, 0.0013]        | 24,421    | 24,421        |
| Bank Marketing       | Logistic regression  | Negative loss    | 0.5021 [0.4967, 0.5078] | 0.0102 [0.0084, 0.0130]      | 0.0014 [0.0005, 0.0023]        | 20,594    | 20,594        |
| Bank Marketing       | HistGradientBoosting | Modified entropy | 0.5122 [0.5068, 0.5176] | 0.0121 [0.0101, 0.0148]      | 0.0014 [0.0007, 0.0021]        | 20,594    | 20,594        |
| Bank Marketing       | Random Forest        | Negative loss    | 0.6597 [0.6542, 0.6648] | 0.0250 [0.0235, 0.0266]      | 0.0025 [0.0024, 0.0027]        | 20,594    | 20,594        |
| Bank Marketing       | ExtraTrees           | Negative loss    | 0.8807 [0.8779, 0.8838] | 0.0437 [0.0426, 0.0448]      | 0.0044 [0.0043, 0.0045]        | 20,594    | 20,594        |
| Bank Marketing       | Small MLP            | Modified entropy | 0.5071 [0.5015, 0.5127] | 0.0116 [0.0089, 0.0135]      | 0.0011 [0.0005, 0.0017]        | 20,594    | 20,594        |
| Diabetes Readmission | Logistic regression  | Negative loss    | 0.5038 [0.5005, 0.5074] | 0.0106 [0.0095, 0.0118]      | 0.0010 [0.0006, 0.0015]        | 50,883    | 50,883        |
| Diabetes Readmission | HistGradientBoosting | Negative loss    | 0.5069 [0.5031, 0.5106] | 0.0097 [0.0086, 0.0108]      | 0.0012 [0.0008, 0.0017]        | 50,883    | 50,883        |
| Diabetes Readmission | Random Forest        | Modified entropy | 0.7990 [0.7963, 0.8018] | 0.1158 [0.1083, 0.1235]      | 0.0126 [0.0100, 0.0164]        | 50,883    | 50,883        |
| Diabetes Readmission | ExtraTrees           | Negative loss    | 0.9982 [0.9979, 0.9985] | 1.0000 [1.0000, 1.0000]      | 0.2780 [0.2435, 0.3221]        | 50,883    | 50,883        |
| Diabetes Readmission | Small MLP            | Modified entropy | 0.5103 [0.5067, 0.5139] | 0.0113 [0.0100, 0.0130]      | 0.0017 [0.0011, 0.0022]        | 50,883    | 50,883        |
