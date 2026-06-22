# Release Route and Licence Plan

Date: 2026-06-04

Status: selected route and licence/reuse plan for the arXiv submission-prep package. Zenodo DOI reserved as https://doi.org/10.5281/zenodo.20552369; publish the Zenodo record before or at the same time as any public manuscript version that cites this DOI.

## Selected Release Route

Use a versioned public code release archived to Zenodo as the preferred route.

Planned route:

1. Create or use a public GitHub repository for the project code and lightweight manuscript-support files.
2. Tag the submission-prep release as `v1.0-submission` or a similarly stable version tag.
3. Archive that release to Zenodo and add the minted Zenodo DOI to the Data Availability and Code Availability statements.
4. Put large generated artifacts in the Zenodo record rather than in the Git repository.
5. If GitHub cannot be made public, use a Zenodo-only record with the same manifest, release notes and file mapping.

Reviewer route:

- If the repository must remain private during review, provide a private reviewer link or anonymized archival review link where the target venue permits it.
- Replace reviewer-only links with public DOI/release URLs before final publication.

## Data Inclusion Decision

Raw third-party datasets:

- Do not redistribute raw third-party public datasets by default.
- Cite the UCI and scikit-learn sources in the Data Availability statement.
- Keep local provenance, checksums and preprocessing records in the release manifest.

Processed and generated project artifacts:

- Include deterministic member/non-member split metadata, processed/split arrays when upstream terms permit redistribution, score-array examples, final manuscript tables, appendix tables, figure source data, QA records and reproducibility manifests in the archival record.
- Host large generated result artifacts, especially the expanded-stage outputs under `analysis/results/`, as one or more Zenodo files if size limits and upload time are acceptable.
- If very large intermediate files are omitted, provide regeneration commands, expected output counts and checksums or manifests for verification.

Manuscript package:

- Keep `release/manuscript_package/` as the near-final review package, not as the complete public data archive.
- The package should point to the archival release once DOI/release URLs exist.

## Licence and Reuse Plan

Code:

- Planned licence: MIT License for project-authored code, unless the owner or institution requires a different licence before deposit.

Generated figures, tables, manifests and project-authored documentation:

- Planned reuse term: CC BY 4.0, unless the owner or institution requires a different term before deposit.

Third-party raw datasets:

- No new licence is asserted over third-party raw datasets.
- Readers should follow the upstream UCI or scikit-learn source terms and citation requirements.

Processed data derived from third-party datasets:

- Release processed/split arrays only where upstream terms allow redistribution.
- If redistribution is uncertain, release the preprocessing code, deterministic split policy, metadata, checksums and regeneration instructions instead.

## Container Decision

Do not add a container recipe for the current release claim.

Rationale:

- The manuscript currently claims a pinned-lock audit-tool smoke path and documents full-grid reproduction commands.
- The pinned clean-environment smoke already validates the score-array audit-reporting path.
- A container is only needed if the release promises full expanded-grid cross-platform reproduction, which is outside the current close-out claim.

## Fields Still Pending Actual Deposit

- Zenodo record must be published before the DOI appears in public.
- Final public GitHub repository URL, if a separate GitHub mirror is later created.

## Chinese Author Check

- 当前选择的路线是：Zenodo reproducibility package，DOI 为 https://doi.org/10.5281/zenodo.20552369。
- 不默认重新发布 UCI / scikit-learn 原始数据，只引用原始来源。
- 大型结果文件不塞进 Git repo，优先放 Zenodo；若太大或不必要，则用命令、manifest、expected counts 和 checksums 支持再生成。
- licence 是 code 用 MIT，项目生成的表格/图/manifest/文档用 CC BY 4.0；第三方 raw data 不套用新的 licence。
