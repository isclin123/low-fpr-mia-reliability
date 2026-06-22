# Table 1. Dataset and audit-split summary

Source: logistic-regression metadata from `expanded_tabular_stage1`; the split is identical across target models.

| Dataset              | Prediction task                      | Rows    |   Features |   Classes | Members   | Non-members   | Audit split                             |
|:---------------------|:-------------------------------------|:--------|-----------:|----------:|:----------|:--------------|:----------------------------------------|
| Credit Default       | Default payment prediction           | 30,000  |         23 |         2 | 15,000    | 15,000        | 50% member / 50% non-member audit split |
| Covertype            | Forest cover type classification     | 581,012 |         54 |         7 | 290,506   | 290,506       | 50% member / 50% non-member audit split |
| Adult Income         | Income threshold prediction          | 48,842  |        108 |         2 | 24,421    | 24,421        | 50% member / 50% non-member audit split |
| Bank Marketing       | Term-deposit subscription prediction | 41,188  |         62 |         2 | 20,594    | 20,594        | 50% member / 50% non-member audit split |
| Diabetes Readmission | Early readmission prediction         | 101,766 |        565 |         2 | 50,883    | 50,883        | 50% member / 50% non-member audit split |
