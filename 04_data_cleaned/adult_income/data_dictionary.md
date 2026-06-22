# Data Dictionary: adult_income

Generated: 2026-06-02T14:26:18-04:00

## Summary

- Description: UCI Adult/Census Income tabular dataset. Original train/test files are combined; categorical unknown markers are kept as an explicit Unknown level.
- Task type: `binary_classification`
- Rows: 48842
- Features: 108
- Target: `income`
- Target classes/counts: `{'0': 37155, '1': 11687}`

## Split

- Random state: `20260602`
- Member/target-train rows: 24421
- Non-member/target-test rows: 24421
- Split rule: 50/50 stratified split; target-train rows are treated as members, held-out target-test rows as non-members.

## Features

| Index | Feature | Stored dtype |
| --- | --- | --- |
| 0 | `age` | `float32` |
| 1 | `fnlwgt` | `float32` |
| 2 | `education_num` | `float32` |
| 3 | `capital_gain` | `float32` |
| 4 | `capital_loss` | `float32` |
| 5 | `hours_per_week` | `float32` |
| 6 | `workclass_Federal-gov` | `float32` |
| 7 | `workclass_Local-gov` | `float32` |
| 8 | `workclass_Never-worked` | `float32` |
| 9 | `workclass_Private` | `float32` |
| 10 | `workclass_Self-emp-inc` | `float32` |
| 11 | `workclass_Self-emp-not-inc` | `float32` |
| 12 | `workclass_State-gov` | `float32` |
| 13 | `workclass_Unknown` | `float32` |
| 14 | `workclass_Without-pay` | `float32` |
| 15 | `education_10th` | `float32` |
| 16 | `education_11th` | `float32` |
| 17 | `education_12th` | `float32` |
| 18 | `education_1st-4th` | `float32` |
| 19 | `education_5th-6th` | `float32` |
| 20 | `education_7th-8th` | `float32` |
| 21 | `education_9th` | `float32` |
| 22 | `education_Assoc-acdm` | `float32` |
| 23 | `education_Assoc-voc` | `float32` |
| 24 | `education_Bachelors` | `float32` |
| 25 | `education_Doctorate` | `float32` |
| 26 | `education_HS-grad` | `float32` |
| 27 | `education_Masters` | `float32` |
| 28 | `education_Preschool` | `float32` |
| 29 | `education_Prof-school` | `float32` |
| 30 | `education_Some-college` | `float32` |
| 31 | `marital_status_Divorced` | `float32` |
| 32 | `marital_status_Married-AF-spouse` | `float32` |
| 33 | `marital_status_Married-civ-spouse` | `float32` |
| 34 | `marital_status_Married-spouse-absent` | `float32` |
| 35 | `marital_status_Never-married` | `float32` |
| 36 | `marital_status_Separated` | `float32` |
| 37 | `marital_status_Widowed` | `float32` |
| 38 | `occupation_Adm-clerical` | `float32` |
| 39 | `occupation_Armed-Forces` | `float32` |
| 40 | `occupation_Craft-repair` | `float32` |
| 41 | `occupation_Exec-managerial` | `float32` |
| 42 | `occupation_Farming-fishing` | `float32` |
| 43 | `occupation_Handlers-cleaners` | `float32` |
| 44 | `occupation_Machine-op-inspct` | `float32` |
| 45 | `occupation_Other-service` | `float32` |
| 46 | `occupation_Priv-house-serv` | `float32` |
| 47 | `occupation_Prof-specialty` | `float32` |
| 48 | `occupation_Protective-serv` | `float32` |
| 49 | `occupation_Sales` | `float32` |
| 50 | `occupation_Tech-support` | `float32` |
| 51 | `occupation_Transport-moving` | `float32` |
| 52 | `occupation_Unknown` | `float32` |
| 53 | `relationship_Husband` | `float32` |
| 54 | `relationship_Not-in-family` | `float32` |
| 55 | `relationship_Other-relative` | `float32` |
| 56 | `relationship_Own-child` | `float32` |
| 57 | `relationship_Unmarried` | `float32` |
| 58 | `relationship_Wife` | `float32` |
| 59 | `race_Amer-Indian-Eskimo` | `float32` |
| 60 | `race_Asian-Pac-Islander` | `float32` |
| 61 | `race_Black` | `float32` |
| 62 | `race_Other` | `float32` |
| 63 | `race_White` | `float32` |
| 64 | `sex_Female` | `float32` |
| 65 | `sex_Male` | `float32` |
| 66 | `native_country_Cambodia` | `float32` |
| 67 | `native_country_Canada` | `float32` |
| 68 | `native_country_China` | `float32` |
| 69 | `native_country_Columbia` | `float32` |
| 70 | `native_country_Cuba` | `float32` |
| 71 | `native_country_Dominican-Republic` | `float32` |
| 72 | `native_country_Ecuador` | `float32` |
| 73 | `native_country_El-Salvador` | `float32` |
| 74 | `native_country_England` | `float32` |
| 75 | `native_country_France` | `float32` |
| 76 | `native_country_Germany` | `float32` |
| 77 | `native_country_Greece` | `float32` |
| 78 | `native_country_Guatemala` | `float32` |
| 79 | `native_country_Haiti` | `float32` |
| 80 | `native_country_Holand-Netherlands` | `float32` |
| 81 | `native_country_Honduras` | `float32` |
| 82 | `native_country_Hong` | `float32` |
| 83 | `native_country_Hungary` | `float32` |
| 84 | `native_country_India` | `float32` |
| 85 | `native_country_Iran` | `float32` |
| 86 | `native_country_Ireland` | `float32` |
| 87 | `native_country_Italy` | `float32` |
| 88 | `native_country_Jamaica` | `float32` |
| 89 | `native_country_Japan` | `float32` |
| 90 | `native_country_Laos` | `float32` |
| 91 | `native_country_Mexico` | `float32` |
| 92 | `native_country_Nicaragua` | `float32` |
| 93 | `native_country_Outlying-US(Guam-USVI-etc)` | `float32` |
| 94 | `native_country_Peru` | `float32` |
| 95 | `native_country_Philippines` | `float32` |
| 96 | `native_country_Poland` | `float32` |
| 97 | `native_country_Portugal` | `float32` |
| 98 | `native_country_Puerto-Rico` | `float32` |
| 99 | `native_country_Scotland` | `float32` |
| 100 | `native_country_South` | `float32` |
| 101 | `native_country_Taiwan` | `float32` |
| 102 | `native_country_Thailand` | `float32` |
| 103 | `native_country_Trinadad&Tobago` | `float32` |
| 104 | `native_country_United-States` | `float32` |
| 105 | `native_country_Unknown` | `float32` |
| 106 | `native_country_Vietnam` | `float32` |
| 107 | `native_country_Yugoslavia` | `float32` |
