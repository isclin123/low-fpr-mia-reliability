# Preprocessing Log

Last updated: 2026-06-02T14:26:20-04:00

## Shared Split Policy

- Each dataset is split into target-train/member and target-test/non-member pools.
- Split ratio: 50/50.
- Stratification: by target label.
- Random state: `20260602`.
- Raw files are not manually edited.

## credit_default

- Raw path: `03_data_raw/credit_default/default of credit card clients.xls`
- Cleaned dataset: `04_data_cleaned/credit_default/cleaned_dataset.npz`
- Split file: `04_data_cleaned/credit_default/member_nonmember_split.npz`
- Rows: 30000
- Features: 23
- Target: `default payment next month`
- Class counts: `{'0': 23364, '1': 6636}`
- Member rows: 15000
- Non-member rows: 15000

## covertype

- Raw path: `03_data_raw/covertype/covertype_raw_arrays.npz`
- Cleaned dataset: `04_data_cleaned/covertype/cleaned_dataset.npz`
- Split file: `04_data_cleaned/covertype/member_nonmember_split.npz`
- Rows: 581012
- Features: 54
- Target: `cover_type`
- Class counts: `{'1': 211840, '2': 283301, '3': 35754, '4': 2747, '5': 9493, '6': 17367, '7': 20510}`
- Member rows: 290506
- Non-member rows: 290506

## adult_income

- Raw path: `03_data_raw/adult_income/adult.zip`
- Cleaned dataset: `04_data_cleaned/adult_income/cleaned_dataset.npz`
- Split file: `04_data_cleaned/adult_income/member_nonmember_split.npz`
- Rows: 48842
- Features: 108
- Target: `income`
- Class counts: `{'0': 37155, '1': 11687}`
- Member rows: 24421
- Non-member rows: 24421

## bank_marketing

- Raw path: `03_data_raw/bank_marketing/bank-additional/bank-additional-full.csv`
- Cleaned dataset: `04_data_cleaned/bank_marketing/cleaned_dataset.npz`
- Split file: `04_data_cleaned/bank_marketing/member_nonmember_split.npz`
- Rows: 41188
- Features: 62
- Target: `y`
- Class counts: `{'0': 36548, '1': 4640}`
- Member rows: 20594
- Non-member rows: 20594

## diabetes_readmission

- Raw path: `03_data_raw/diabetes_readmission/diabetic_data.csv`
- Cleaned dataset: `04_data_cleaned/diabetes_readmission/cleaned_dataset.npz`
- Split file: `04_data_cleaned/diabetes_readmission/member_nonmember_split.npz`
- Rows: 101766
- Features: 565
- Target: `readmitted`
- Class counts: `{'0': 90409, '1': 11357}`
- Member rows: 50883
- Non-member rows: 50883
