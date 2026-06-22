# Finite-Sample Reliability of Low-FPR Membership Inference Audits: Reproducibility Package

Version: v1.0.0

Date: 2026-06-05

Creator: Sicheng Yi

DOI: https://doi.org/10.5281/zenodo.20552369

Preprint DOI: https://doi.org/10.5281/zenodo.20552862

This archive supports the manuscript "Finite-Sample Reliability of Low-FPR Membership Inference Audits". It contains the project-authored code, reproduction commands, lightweight processed/split arrays, score arrays, final derived tables, figure source outputs, appendix-check outputs, and manuscript-support documentation needed to inspect the reported finite-sample low-FPR membership-inference audit results.

## Scope

The archive supports the arXiv submission version of the manuscript. It is intended as a durable reproducibility package, not as a redistribution of the original third-party raw datasets.

Included materials:

- analysis code and reusable score-array audit tooling under `05_analysis/`;
- dependency files, smoke examples, configs, and reproduction commands;
- cleaned/split arrays and metadata under `04_data_cleaned/`;
- main expanded-grid score arrays, metrics, confidence intervals, subsampling outputs, and sample-size requirement summaries, excluding trained model caches;
- final main tables, appendix tables, expanded figures, Q1 appendix figures, diagnostics, and figure captions under `06_figures_tables/`;
- Q1 reference-centered score, bounded shadow-model score, tie-rule, split/seed, label-uncertainty, ExtraTrees sanity, and final CI hardening outputs;
- final manuscript PDF/TeX for traceability.

Excluded materials:

- raw third-party dataset files from UCI or scikit-learn;
- trained model cache files under `05_analysis/results/*/models/`, which are large and regenerable from documented commands;
- transient build files, Python caches, and local temporary files.
- packaged submission zip files, which are omitted from this GitHub mirror because the archival release is already available on Zenodo.

## Reproduction Entry Points

Start with:

- `09_final/reproducibility_package/README.md`
- `09_final/reproducibility_package/environment.md`
- `09_final/reproducibility_package/commands.md`
- `09_final/reproducibility_package/data_and_outputs_manifest.md`

The main command file documents the fast smoke path, expanded tabular run, final confidence-interval hardening, final table/figure generation, reference-centered compatibility check, bounded shadow-model score-array check, tie-rule sensitivity check, split/seed sensitivity check, and label-uncertainty check.

## Data and Licence Notes

The original raw datasets are public third-party datasets and should be obtained and cited through their source repositories. This archive does not claim a new licence over those raw datasets or over upstream dataset content. Processed/split arrays are included only to support reproducibility and remain subject to upstream dataset terms where applicable.

Project-authored code is released under the MIT License. Project-authored documentation, generated figures, tables, manifests, and figure/table source data are released under CC BY 4.0 unless a file states otherwise. See `NOTICE.md`, `LICENSE_MIT.txt`, and the release notes for details.

## Citation

If you use this reproducibility package, cite the archived Zenodo record:

Yi, Sicheng. Finite-Sample Reliability of Low-FPR Membership Inference Audits: Reproducibility Package. Zenodo. https://doi.org/10.5281/zenodo.20552369

Associated preprint:

Yi, Sicheng. Finite-Sample Reliability of Low-FPR Membership Inference Audits. Zenodo. https://doi.org/10.5281/zenodo.20552862
