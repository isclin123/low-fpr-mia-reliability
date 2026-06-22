# Reproducibility Package Draft

Date: 2026-06-05

Project: Reliable Statistical Evaluation of Membership Inference Attacks under Limited Audit Samples

Status: Zenodo reproducibility package prepared for public release at
https://doi.org/10.5281/zenodo.20552369. The Zenodo record must be published
before or at the same time as any public manuscript version that cites this DOI.
The package can be reproduced locally from the documented commands, seeds,
parameters, expected row counts, and output paths.

## Scope

This package records how to reproduce the current empirical evidence and audit-tool outputs for the manuscript draft. It is a manifest and command guide, not a compact archive of all raw data and result files.

The package covers:

- five public tabular datasets;
- five sklearn-compatible target-model families;
- four simple score-based MIA scores;
- AUC, TPR@1%FPR, TPR@0.1%FPR, and membership advantage;
- stratified bootstrap intervals;
- fixed-threshold Wilson intervals through the audit tool;
- repeated balanced audit subsampling;
- tail-resolution warnings;
- final main/appendix tables and expanded figures;
- Q1 reference-centered score compatibility check;
- Q1 bounded shadow-model score-array check;
- Q1 tie-rule sensitivity check;
- Q1 split/seed sensitivity check;
- Q1 label-corruption check for observed audit labels.

## Files in This Package

| File | Purpose |
|---|---|
| `environment.md` | Python/runtime requirements and observed package versions. |
| `commands.md` | Commands for smoke, expanded, hardening, figure, and table reproduction. |
| `data_and_outputs_manifest.md` | Data provenance, config files, scripts, and expected result locations. |
| `smoke_reproduction.md` | Fast reproduction path using the audit-tool NPZ/CSV examples. |
| `clean_env_smoke.md` | Clean virtual-environment smoke-test record for the audit-tool examples. |
| `locked_env_smoke.md` | Pinned-lock clean virtual-environment smoke-test record for the audit-tool examples. |
| `minimum_reproducible_artifact.md` | Smallest reviewer-facing artifact path for the score-array reporting layer. |
| `release_checklist.md` | Items still needed before a public archival release. |
| `release_licence_notes.md` | Planned public release route, code licence and data/output reuse notes. |

## Current Evidence Boundary

The full expanded stage1 grid uses 50 bootstrap repeats and supports broad pattern finding and appendix exploration. Main manuscript intervals use the selected final CI hardening run with 1,000 bootstrap repeats for main-table candidate rows.

Do not describe the full 500-row appendix CI grid as hardened unless it is rerun with the final hardening procedure.

## Primary Reproduction Paths

Use the short path first:

1. Install the locked environment in `environment.md`.
2. Read the minimum artifact checklist in `minimum_reproducible_artifact.md`.
3. Run the audit-tool examples in `smoke_reproduction.md`.
4. Check the clean-environment smoke records in `clean_env_smoke.md` and `locked_env_smoke.md`.
5. Regenerate final figures/tables with the commands in `commands.md`.
6. Run the Q1 reference-centered, bounded shadow-model, tie-rule, split/seed,
   and label-corruption checks in `commands.md` when reviewing the appendix
   robustness checks.
7. For full empirical reproduction, rerun `expanded_tabular_stage1` and selected final CI hardening.

## Important Non-Claims

The Q1 reference-centered and bounded shadow-model score checks are bounded
compatibility checks, not LiRA/RMIA benchmarks or attack rankings. The tie-rule
and split/seed checks are representative sensitivity checks, not exhaustive
reruns of the full grid. The package does not reproduce formal LiRA, RMIA,
calibrated-score attacks, text-model pilots, language-model membership
inference, or production privacy audits. Those are outside the active
manuscript scope.

## Public Release Route

The selected route for the arXiv version is a Zenodo reproducibility package:
https://doi.org/10.5281/zenodo.20552369. Raw third-party datasets should be
cited through UCI/scikit-learn rather than redistributed by default. Large
trained-model cache files are excluded from the archive and regenerated from
the documented commands rather than deposited as static artifacts.

Licence/reuse terms are MIT for project-authored code and CC BY 4.0 for project-authored generated figures, tables, manifests and documentation.
