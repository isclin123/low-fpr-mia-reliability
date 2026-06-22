# Data Dictionary: bank_marketing

Generated: 2026-06-02T14:26:18-04:00

## Summary

- Description: UCI Bank Marketing additional-full tabular dataset. The post-call duration feature is excluded because it is not available before the outcome is known.
- Task type: `binary_classification`
- Rows: 41188
- Features: 62
- Target: `y`
- Target classes/counts: `{'0': 36548, '1': 4640}`

## Split

- Random state: `20260602`
- Member/target-train rows: 20594
- Non-member/target-test rows: 20594
- Split rule: 50/50 stratified split; target-train rows are treated as members, held-out target-test rows as non-members.

## Features

| Index | Feature | Stored dtype |
| --- | --- | --- |
| 0 | `age` | `float32` |
| 1 | `campaign` | `float32` |
| 2 | `pdays` | `float32` |
| 3 | `previous` | `float32` |
| 4 | `emp.var.rate` | `float32` |
| 5 | `cons.price.idx` | `float32` |
| 6 | `cons.conf.idx` | `float32` |
| 7 | `euribor3m` | `float32` |
| 8 | `nr.employed` | `float32` |
| 9 | `job_admin.` | `float32` |
| 10 | `job_blue-collar` | `float32` |
| 11 | `job_entrepreneur` | `float32` |
| 12 | `job_housemaid` | `float32` |
| 13 | `job_management` | `float32` |
| 14 | `job_retired` | `float32` |
| 15 | `job_self-employed` | `float32` |
| 16 | `job_services` | `float32` |
| 17 | `job_student` | `float32` |
| 18 | `job_technician` | `float32` |
| 19 | `job_unemployed` | `float32` |
| 20 | `job_unknown` | `float32` |
| 21 | `marital_divorced` | `float32` |
| 22 | `marital_married` | `float32` |
| 23 | `marital_single` | `float32` |
| 24 | `marital_unknown` | `float32` |
| 25 | `education_basic.4y` | `float32` |
| 26 | `education_basic.6y` | `float32` |
| 27 | `education_basic.9y` | `float32` |
| 28 | `education_high.school` | `float32` |
| 29 | `education_illiterate` | `float32` |
| 30 | `education_professional.course` | `float32` |
| 31 | `education_university.degree` | `float32` |
| 32 | `education_unknown` | `float32` |
| 33 | `default_no` | `float32` |
| 34 | `default_unknown` | `float32` |
| 35 | `default_yes` | `float32` |
| 36 | `housing_no` | `float32` |
| 37 | `housing_unknown` | `float32` |
| 38 | `housing_yes` | `float32` |
| 39 | `loan_no` | `float32` |
| 40 | `loan_unknown` | `float32` |
| 41 | `loan_yes` | `float32` |
| 42 | `contact_cellular` | `float32` |
| 43 | `contact_telephone` | `float32` |
| 44 | `month_apr` | `float32` |
| 45 | `month_aug` | `float32` |
| 46 | `month_dec` | `float32` |
| 47 | `month_jul` | `float32` |
| 48 | `month_jun` | `float32` |
| 49 | `month_mar` | `float32` |
| 50 | `month_may` | `float32` |
| 51 | `month_nov` | `float32` |
| 52 | `month_oct` | `float32` |
| 53 | `month_sep` | `float32` |
| 54 | `day_of_week_fri` | `float32` |
| 55 | `day_of_week_mon` | `float32` |
| 56 | `day_of_week_thu` | `float32` |
| 57 | `day_of_week_tue` | `float32` |
| 58 | `day_of_week_wed` | `float32` |
| 59 | `poutcome_failure` | `float32` |
| 60 | `poutcome_nonexistent` | `float32` |
| 61 | `poutcome_success` | `float32` |
