# Data and Code Availability Statement

Date: 2026-06-04

Status: final arXiv availability wording after Zenodo DOI reservation. The Zenodo record must be published before or at the time this DOI appears in the public manuscript.

## Data Availability

This study used five publicly available tabular datasets. The Default of Credit Card Clients dataset is available from the UCI Machine Learning Repository at https://doi.org/10.24432/C55S3H. The Adult dataset is available from the UCI Machine Learning Repository at https://doi.org/10.24432/C5XW20. The Bank Marketing dataset is available from the UCI Machine Learning Repository at https://doi.org/10.24432/C5K306. The Diabetes 130-US Hospitals for Years 1999-2008 dataset is available from the UCI Machine Learning Repository at https://doi.org/10.24432/C5230J. The Forest Covertype dataset was obtained using `sklearn.datasets.fetch_covtype`; the scikit-learn documentation describes the dataset as 581,012 samples, 54 features and 7 classes.

The processed arrays, deterministic member/non-member split files, attack-score arrays, metric tables, confidence-interval tables, audit-subsampling outputs, final table CSV files, appendix table CSV files and figure source data generated in this study are archived in the Zenodo reproducibility package at https://doi.org/10.5281/zenodo.20552369. The release excludes large trained-model cache files, which are regenerable from the documented commands, seeds, parameters and output paths. Data provenance, checksums for downloaded raw files, preprocessing notes and output manifests are recorded in `data_sources/data_sources.md`, `data_processed/preprocessing_log.md` and `release/reproducibility_package/data_and_outputs_manifest.md`.

Raw third-party public datasets should be cited through their source repositories rather than treated as newly generated data. The archival project record should therefore contain the processed/split data and generated analysis outputs required to reproduce the manuscript results where redistribution terms permit, while directing readers to the original UCI and scikit-learn sources for the raw datasets. If redistribution of any processed derivative is uncertain, the release should provide preprocessing scripts, deterministic split policy, metadata, checksums and regeneration instructions instead of redistributing that file.

## Code Availability

Code for data preprocessing, target-model training, attack-score extraction, membership-inference metric calculation, stratified bootstrap intervals, fixed-threshold Wilson intervals, audit-sample-size sensitivity analysis, reusable score-array audit reports, final confidence-interval hardening and figure/table generation is archived in the Zenodo reproducibility package at https://doi.org/10.5281/zenodo.20552369.

The current code is organized under `analysis/`. The main entry points are `analysis/run_experiment.py`, `analysis/run_audit_tool.py`, `analysis/run_final_ci_hardening.py`, `analysis/generate_expanded_outputs.py` and `analysis/generate_final_tables.py`. Reproduction commands, environment notes, clean-environment smoke-test records and the minimum reproducible artifact path are documented in `release/reproducibility_package/`.

## Repository, Licence and Citation Actions

- Publish the Zenodo record before or at the same time as the arXiv version that cites it.
- DOI for data/code artifact: https://doi.org/10.5281/zenodo.20552369.
- Code licence: MIT License for project-authored code.
- Generated-output reuse term: CC BY 4.0 for project-authored documentation, generated figures/tables, manifests, QA records and figure/table source data.
- Do not apply a new open licence to third-party raw datasets unless the authors have redistribution rights.
- Include README metadata, file manifest, script-to-output mapping and checksums for large generated artifacts.
- Provide a private reviewer link if the repository remains private during review.
- Release route and licence details are recorded in `release/release_route_and_licence_plan.md` and `release/reproducibility_package/release_licence_notes.md`.

## FAIR / Metadata Audit

Current status:

- Findable: ready once the Zenodo record is published. Local manifests and paths exist, and the DOI is https://doi.org/10.5281/zenodo.20552369.
- Accessible: partial. Public raw data sources are accessible through UCI/scikit-learn; generated processed data and outputs still need the planned public archival access route.
- Interoperable: good for local review. Files use CSV, Markdown, JSON, NPZ, PNG, SVG and PDF, with data dictionaries and manifests.
- Reusable: ready once the Zenodo record is published. Provenance, commands, clean-smoke records, pinned-lock smoke records and licence/reuse notes are included.

## Missing Information / Risk Flags

- Publish the Zenodo record before citing the DOI in a public manuscript version.
- Final public GitHub repository URL, if a separate GitHub mirror is later created.
- Public-release validation beyond the fast audit-tool smoke path only if the release promises full expanded-grid reproduction across platforms.

## 中文核对

- 当前英文声明已经能说明：用了哪些公开数据、生成了哪些 processed/result/source-data artifacts、代码在哪里、选择哪条 public release route，以及 licence/reuse plan 是什么。
- 当前 DOI：https://doi.org/10.5281/zenodo.20552369。请确保 Zenodo record 在 arXiv 公布前已经 Publish。
- licence：code 用 MIT；项目生成的 figures/tables/manifests/documentation 用 CC BY 4.0；第三方 raw data 不套用新的项目 licence。
- 不建议在正式投稿版里写“available upon request”。这个项目的数据和代码应尽量通过 Zenodo/GitHub release + DOI 公开。
