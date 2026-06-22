# Release Licence and Data-Use Notes

Date: 2026-06-04

Status: public-release notes for the reproducibility package. Zenodo DOI: https://doi.org/10.5281/zenodo.20552369.

## Public Release Route

Preferred route:

- public GitHub repository;
- versioned release tag such as `v1.0-submission`;
- Zenodo archive of the tagged release at https://doi.org/10.5281/zenodo.20552369;
- Zenodo-hosted large generated artifacts where needed.

Fallback route:

- Zenodo-only release if a public GitHub repository cannot be used.

## Code Licence

Planned licence:

- MIT License for project-authored code.

Applies to:

- `05_analysis/src/`
- `05_analysis/run_experiment.py`
- `05_analysis/run_audit_tool.py`
- `05_analysis/run_final_ci_hardening.py`
- `05_analysis/generate_expanded_outputs.py`
- `05_analysis/generate_final_tables.py`
- project-authored helper scripts and examples.

Does not apply to:

- third-party Python packages;
- third-party datasets;
- generated content whose upstream data terms restrict redistribution.

## Data and Output Reuse

Planned reuse term:

- CC BY 4.0 for project-authored documentation, generated manuscript tables, generated figures, manifests, QA records and figure/table source data.

Third-party raw data:

- Do not apply a new project licence to UCI or scikit-learn raw datasets.
- Cite and link upstream sources in the Data Availability statement.
- Release raw data only if upstream terms and repository policy clearly permit redistribution.

Processed/split arrays:

- Release processed/split arrays only if upstream terms allow redistribution.
- If redistribution is uncertain, release preprocessing scripts, deterministic split policy, metadata, checksums and regeneration instructions instead.

Large result artifacts:

- Host large generated outputs in Zenodo rather than Git.
- If full intermediate outputs are omitted, include regeneration commands and expected output counts in `commands.md` and `data_and_outputs_manifest.md`.

## Container Scope

No container recipe is required for the current public claim.

The current claim is:

- pinned-lock audit-tool smoke reproduction validates the score-array reporting path;
- full expanded-grid reproduction commands and expected output counts are documented.

A container recipe should be added only if the release claims full expanded-grid cross-platform reproduction.
