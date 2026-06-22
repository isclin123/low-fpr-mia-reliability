# Reproducibility Release Checklist

Date: 2026-06-04

Status: release-route and licence/reuse plan recorded; Zenodo DOI reserved as https://doi.org/10.5281/zenodo.20552369. Publish the Zenodo record before or at the same time as any public manuscript version that cites this DOI.

## Completed in This Draft

- [x] Document environment requirements.
- [x] Record observed package versions.
- [x] Document data provenance and preprocessing records.
- [x] Document full expanded-run commands.
- [x] Document audit-tool smoke reproduction path.
- [x] Test audit-tool examples in a clean temporary virtual environment.
- [x] Document the minimum reproducible artifact path for the score-array audit layer.
- [x] Document final CI hardening command.
- [x] Document final figure/table generation commands.
- [x] Record expected output counts.
- [x] Link figure/table QA and uncertainty-method notes.
- [x] Draft Data Availability and Code Availability wording.
- [x] Recheck final citation metadata for the near-final manuscript.
- [x] Create a pinned environment lock file.
- [x] Rerun audit-tool smoke validation in a locked clean environment.
- [x] Decide the public release route.
- [x] Add release licence and data-use notes.
- [x] Check for user-specific absolute paths in public-facing release notes.
- [x] Run final claim-support audit.
- [x] Run strong-reviewer pre-submission review.
- [x] Document Q1 reference-centered score check commands, parameters, seed,
  output paths, and expected row counts.
- [x] Document Q1 label-corruption stress-test commands, corruption rates,
  repeat/canonical seeds, output paths, and expected row counts.
- [x] Mark the package as locally reproducible before public DOI reservation;
  final DOI now recorded as https://doi.org/10.5281/zenodo.20552369.

## Needed Before Public Release

- [x] 2026-06-04 Decide whether raw data and large result artifacts are included, regenerated, or externally hosted.
  - Decision: raw third-party datasets are cited through UCI/scikit-learn rather than redistributed by default; processed/split arrays and generated outputs are deposited where redistribution terms permit; large generated result artifacts should be hosted in Zenodo or regenerated from documented commands.
- [x] 2026-06-04 Add licence and data-use notes for public release.
  - Output: `release/reproducibility_package/release_licence_notes.md`
  - Plan: MIT for project-authored code; CC BY 4.0 for project-authored generated figures/tables/manifests/documentation; no new licence asserted over third-party raw datasets.
- [x] 2026-06-04 Remove or relativize local absolute paths from public-facing run summaries if necessary.
  - Status: no user-specific `/Users/...` or workspace absolute paths were found in the release package. Temporary `/tmp/...` smoke-test paths remain as reproducible ephemeral examples.
- [x] Replace earlier Data/Code Availability draft fields with public DOI/release URL and licence fields.
- [ ] Repeat Jebreel et al. 2026 citation check only if PoPETs 2026 Issue 3 appears before submission.
- [ ] Confirm owner/institution approval for MIT code licence and CC BY 4.0 generated-artifact reuse terms before public deposit.

## Known Scope Exclusions

- LiRA/RMIA empirical baselines are not included in the current reproduction package.
- Calibration experiments and reliability diagrams are not included in the active main-manuscript scope.
- Text or small-language-model pilot experiments are not included in the active main-manuscript scope.
- Production privacy-audit claims are not supported by this package.
