# Dataset Selection

Date selected: 2026-06-02

## Core Dataset Decision

The first complete experiment will use two datasets:

1. `credit_default`
2. `covertype`

This pair gives a useful contrast between a privacy-relevant medium-size financial dataset and a large tabular benchmark that can support more reliable low-FPR tail estimation.

## Dataset 1: `credit_default`

- Full name: Default of Credit Card Clients
- Source: UCI Machine Learning Repository
- Source URL: `https://www.archive.ics.uci.edu/ml/datasets/default%2Bof%2Bcredit%2Bcard%2Bclients`
- Dataset ID: 350
- DOI: `10.24432/C55S3H`
- Task: binary classification
- Target: default payment indicator
- Approximate records: 30,000
- Reason for inclusion:
  - Stronger privacy-audit motivation than a generic benchmark.
  - Medium size makes low-FPR uncertainty visible.
- Expected limitation:
  - TPR@0.1%FPR may be unstable for small audit samples because the effective number of non-member tail examples is very small.

## Dataset 2: `covertype`

- Full name: Forest Covertype
- Source: scikit-learn `fetch_covtype`
- Source URL: `https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_covtype.html`
- Task: multiclass classification
- Approximate records: 581,012
- Feature count: 54
- Reason for inclusion:
  - Large enough for more credible 0.1% FPR tail analysis.
  - Provides contrast against `credit_default`.
- Expected limitation:
  - Less directly privacy-sensitive than financial or medical data, so it should be framed as a large-scale statistical benchmark rather than the motivating privacy case.

## Data Storage Plan

- Raw download/cache location: `03_data_raw/`
- Cleaned data and split files: `04_data_cleaned/`
- Data provenance notes: `03_data_raw/data_sources.md`
- Preprocessing log: `04_data_cleaned/preprocessing_log.md`

## Access Plan

- Use programmatic loaders where possible.
- Store enough metadata to reproduce the source, access date, dataset version, target column, and preprocessing decisions.
- Do not manually edit raw dataset files.

## Fallbacks

If `credit_default` access fails:

- Use Adult Income as the fallback medium-size tabular dataset.

If full Covertype is too slow:

- Use a reproducible stratified subset of Covertype.
- Record subset size and seed in `05_analysis/results/core/run_config.json`.
