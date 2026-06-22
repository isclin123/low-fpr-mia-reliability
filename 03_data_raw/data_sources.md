# Data Sources

Last updated: 2026-06-03

## Summary

Core and expanded raw datasets have been downloaded or cached in `03_data_raw/`.

Raw data locations:

- `credit_default`: `03_data_raw/credit_default/`
- `covertype`: `03_data_raw/covertype/`
- `adult_income`: `03_data_raw/adult_income/`
- `bank_marketing`: `03_data_raw/bank_marketing/`
- `diabetes_readmission`: `03_data_raw/diabetes_readmission/`

Cleaned data and reproducible member/non-member splits are available for all five active datasets in `04_data_cleaned/`: `credit_default`, `covertype`, `adult_income`, `bank_marketing`, and `diabetes_readmission`.

## Dataset 1: `credit_default`

- Full name: Default of Credit Card Clients
- Source: UCI Machine Learning Repository
- Source URL: `https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip`
- Dataset page: `https://www.archive.ics.uci.edu/ml/datasets/default%2Bof%2Bcredit%2Bcard%2Bclients`
- Dataset ID: 350
- DOI: `10.24432/C55S3H`
- Access date: 2026-06-02
- Local raw zip: `03_data_raw/credit_default/default_of_credit_card_clients.zip`
- Local extracted file: `03_data_raw/credit_default/default of credit card clients.xls`
- File sizes:
  - zip: 5.3 MB
  - xls: 5.3 MB
- SHA-256:
  - zip: `56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602`
  - xls: `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933`
- Validation:
  - Read with pandas using `header=1`.
  - Shape: 30,000 rows x 25 columns.
  - First columns: `ID`, `LIMIT_BAL`, `SEX`, `EDUCATION`, `MARRIAGE`.
  - Target column: `default payment next month`.
- Dependency note:
  - The raw file is old-style `.xls`; pandas requires `xlrd`.
  - `xlrd` has been added to `05_analysis/requirements.txt`.

## Dataset 2: `covertype`

- Full name: Forest Covertype
- Source: scikit-learn `fetch_covtype`
- Documentation URL: `https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_covtype.html`
- Access date: 2026-06-02
- Local sklearn cache:
  - `03_data_raw/covertype/sklearn_cache/covertype/samples_py3`
  - `03_data_raw/covertype/sklearn_cache/covertype/targets_py3`
- Local compressed raw arrays:
  - `03_data_raw/covertype/covertype_raw_arrays.npz`
- File sizes:
  - `covertype_raw_arrays.npz`: 16 MB
  - `samples_py3`: 14 MB
  - `targets_py3`: 36 KB
- SHA-256:
  - `covertype_raw_arrays.npz`: `bf4442af8fb352a60a0142d29d9bf6ec3b4a54e8de36008b111da51933848577`
  - `samples_py3`: `ba15c20add4a83550488f189a3c4b1d774167e84256d99844d5327f4174323ff`
  - `targets_py3`: `9c41047c16f75a49a2e6852913a504a653892a856ffe8698ba918901a550eee5`
- Validation:
  - Loaded with scikit-learn `fetch_covtype`.
  - Data shape: 581,012 rows x 54 features.
  - Target shape: 581,012 labels.
  - Classes: 1, 2, 3, 4, 5, 6, 7.

## Dataset 3: `adult_income`

- Full name: Adult / Census Income
- Source: UCI Machine Learning Repository
- Source URL: `https://archive.ics.uci.edu/static/public/2/adult.zip`
- Dataset page: `https://archive.ics.uci.edu/dataset/2/adult`
- Dataset ID: 2
- DOI: `10.24432/C5XW20`
- Access date: 2026-06-02
- Local raw zip: `03_data_raw/adult_income/adult.zip`
- Local extracted files:
  - `03_data_raw/adult_income/adult.data`
  - `03_data_raw/adult_income/adult.test`
  - `03_data_raw/adult_income/adult.names`
  - `03_data_raw/adult_income/old.adult.names`
  - `03_data_raw/adult_income/Index`
- File sizes:
  - zip: 608 KB
  - `adult.data`: 3.8 MB
  - `adult.test`: 1.9 MB
- SHA-256:
  - zip: `7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb`
  - `adult.data`: `5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d`
  - `adult.test`: `a2a9044bc167a35b2361efbabec64e89d69ce82d9790d2980119aac5fd7e9c05`
- Validation:
  - Read with pandas using 15 manually assigned columns and `skipinitialspace=True`.
  - Train shape: 32,561 rows x 15 columns.
  - Test shape: 16,281 rows x 15 columns after skipping the leading comment line.
  - Target column: `income`.
  - Train target values: `<=50K`, `>50K`.
  - Test target values include trailing periods and will need normalization during cleaning.

## Dataset 4: `bank_marketing`

- Full name: Bank Marketing
- Source: UCI Machine Learning Repository
- Source URL: `https://archive.ics.uci.edu/static/public/222/bank+marketing.zip`
- Dataset page: `https://archive.ics.uci.edu/dataset/222/bank+marketing`
- Dataset ID: 222
- DOI: `10.24432/C5K306`
- Access date: 2026-06-02
- Local raw zip: `03_data_raw/bank_marketing/bank_marketing.zip`
- Local nested zips:
  - `03_data_raw/bank_marketing/bank.zip`
  - `03_data_raw/bank_marketing/bank-additional.zip`
- Local extracted files:
  - `03_data_raw/bank_marketing/bank-additional/bank-additional-full.csv`
  - `03_data_raw/bank_marketing/bank-additional/bank-additional.csv`
  - `03_data_raw/bank_marketing/bank-additional/bank-additional-names.txt`
  - `03_data_raw/bank_marketing/bank-full.csv`
  - `03_data_raw/bank_marketing/bank.csv`
  - `03_data_raw/bank_marketing/bank-names.txt`
- File sizes:
  - outer zip: 1.0 MB
  - `bank-additional-full.csv`: 5.6 MB
  - `bank-full.csv`: 4.4 MB
- SHA-256:
  - outer zip: `e0bf5f5de5b846e2f18e9d90606637267d46dfa260e0f17bb12e605db5efbeb4`
  - `bank-additional-full.csv`: `74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8`
  - `bank-full.csv`: `d1513ec63b385506f7cfce9f2c5caa9fe99e7ba4e8c3fa264b3aaf0f849ed32d`
- Validation:
  - Read `bank-additional-full.csv` with pandas using semicolon separator.
  - Shape: 41,188 rows x 21 columns.
  - Target column: `y`.
  - Target values: `no`, `yes`.
  - Loader should default to `bank-additional-full.csv` because it is the fuller 20-input version.
  - macOS extraction metadata (`__MACOSX`, `.DS_Store`) and `.Rhistory` were removed after extraction; original zip files are retained.

## Dataset 5: `diabetes_readmission`

- Full name: Diabetes 130-US Hospitals for Years 1999-2008
- Source: UCI Machine Learning Repository
- Source URL: `https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip`
- Dataset page: `https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for-years+1999-2008`
- Dataset ID: 296
- DOI: `10.24432/C5230J`
- Access date: 2026-06-02
- Local raw zip: `03_data_raw/diabetes_readmission/diabetes_130_us_hospitals.zip`
- Local extracted files:
  - `03_data_raw/diabetes_readmission/diabetic_data.csv`
  - `03_data_raw/diabetes_readmission/IDS_mapping.csv`
- File sizes:
  - zip: 3.0 MB
  - `diabetic_data.csv`: 18 MB
  - `IDS_mapping.csv`: 4 KB
- SHA-256:
  - zip: `f82ac129da2ddd2299391ff6fbae3a6a58b3edcf59ac9d7bd480c00fe453112a`
  - `diabetic_data.csv`: `0689e7ec031237dc63031b938805c48377748761a3b26acab621567afa24df97`
  - `IDS_mapping.csv`: `f1bb82b471cb34649352597572c9b1fb00bd27f77b9f5a22a03dc3eb1039749e`
- Validation:
  - Read `diabetic_data.csv` with pandas.
  - Shape: 101,766 rows x 50 columns.
  - Target candidate: `readmitted`.
  - Target values: `<30`, `>30`, `NO`.
  - Read `IDS_mapping.csv`; shape: 67 rows x 2 columns.
  - Loader must define the classification target carefully, likely `<30` versus not `<30` for 30-day readmission.

## Current Process Status

Dataset loading and preprocessing have been implemented in `05_analysis/src/mia_eval/data.py`.

Cleaned core outputs:

- `04_data_cleaned/credit_default/cleaned_dataset.npz`
- `04_data_cleaned/credit_default/member_nonmember_split.npz`
- `04_data_cleaned/covertype/cleaned_dataset.npz`
- `04_data_cleaned/covertype/member_nonmember_split.npz`

Preprocessing details are recorded in `04_data_cleaned/preprocessing_log.md`.

Expanded raw downloads, dataset loaders, cleaned arrays, and member/non-member splits are complete for `adult_income`, `bank_marketing`, and `diabetes_readmission`.
