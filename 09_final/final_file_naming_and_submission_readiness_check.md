# Final File Naming and Submission-Readiness Check

Date: 2026-06-05

Status: arXiv source-upload pass for the active Q1 internal package. The package is coherently named, rendered, content-gated, independently zip-compiled, and updated with the Zenodo reproducibility-package DOI `https://doi.org/10.5281/zenodo.20552369`; the Zenodo record must be published before or at the same time as the public arXiv version that cites it.

## 2026-06-04 Format Addendum

The Q1 proof was rechecked under a stricter Nature-style/high-impact-paper layout standard after the author field was added. It was then updated again on 2026-06-05 after multi-agent content review for novelty clarity, method/statistical boundaries, Appendix F scope, and results-storyline hardening, completed with bounded shadow-model, tie-rule, and split/seed appendices, and finally polished for table order/spacing and appendix diagnostic figures. It was recompiled as the active 24-page proof.

| Item | Path | Result |
|---|---|---|
| Nature-style PDF format review | `08_reviews_revisions/q1_nature_pdf_format_review.md` | Pass for internal Q1-ready proof |
| Author block | `09_final/manuscript_package/manuscript_q1.tex` | `Sicheng Yi` present in source and PDF metadata |
| Canonical Q1 draft author line | `07_drafts/full_draft_q1.md` | `Sicheng Yi` present |
| Package Q1 Markdown author line | `09_final/manuscript_package/manuscript_q1.md` | `Sicheng Yi` present |
| Figure 4 tail-evidence repair | `09_final/manuscript_package/manuscript_q1.tex` | Figure 4 now shows TPR@0.1%FPR audit-size uncertainty rather than the less central AUC-width diagnostic |
| Citation rendering repair | `09_final/manuscript_package/manuscript_q1.tex` | Pseudo-citations replaced by bracket numeric citations with internal reference anchors |

Additional validation after the current Q1 repair and reliability-positioning update:

- `latexmk -xelatex` completed successfully for `manuscript_q1.tex`.
- PDF page-count checks returned 24 pages.
- `proofs/rendered_pages_q1/` contains 24 page PNGs.
- Final focused LaTeX log scan found no fatal errors, LaTeX errors, undefined control sequences, undefined references, citation/reference undefined warnings, overfull boxes, float-too-large errors, missing characters, or rerun cross-reference warnings.
- Visual review of the rendered pages, including the corrected Table 1/Table 2 flow, the captioned gap/AUC table, and updated appendix pages 21-24, found no missing figures, black blocks, clipping, table overlap, abstract truncation, or split supplemental-check list.
- Citation-link validation confirmed internal reference jumps during the citation-link repair pass; the current compile has no undefined references or citation warnings, and page 1 displays clean bracket numeric citation markers without visible braces or LaTeX syntax.
- Jälkö et al. 2026 remains cited for the efficient-MIA-evaluation reliability boundary; additional adjacent references were added for MIA-as-privacy-tool reliability, sample complexity, full-pipeline auditing/tooling, ML-Leaks, and Gaussian membership-inference privacy context.
- The novelty-framing revision now identifies finite-sample low-FPR reliability as the paper-level post-score reporting problem and makes the mini audit supporting evidence rather than the sole basis of the contribution.
- Appendix F is narrowed to a reference-centered score-array compatibility check, not a stronger-attack, LiRA/RMIA, or attack-ranking benchmark.
- The arXiv upload zip was rebuilt and independently compiled after extraction to a 24-page PDF after the Zenodo DOI availability pass.

Boundary: this is a coherent arXiv-ready Q1 proof, not a target-journal final submission template. A specific journal template plus affiliation/email/corresponding-author details are still needed before journal submission. The external action that remains for the arXiv version is to publish the Zenodo record before citing the DOI publicly.

## Q1 Update Addendum

The active package source is now the Q1 LaTeX final-source candidate:

| Item | Path | Result |
|---|---|---|
| Canonical Q1 manuscript source | `07_drafts/full_draft_q1.md` | Present |
| Package Q1 Markdown bridge | `09_final/manuscript_package/manuscript_q1.md` | Present |
| Package Q1 LaTeX source | `09_final/manuscript_package/manuscript_q1.tex` | Present |
| Q1 PDF proof | `09_final/manuscript_package/proofs/manuscript_q1.pdf` | Present |
| Q1 rendered proof pages | `09_final/manuscript_package/proofs/rendered_pages_q1/page-01.png` through `page-24.png` | 24 pages present |
| Q1 proof QA | `09_final/manuscript_package/proofs/manuscript_q1_latex_proof_qa.md` | Present |
| Flattened Q1 figure rasters | `09_final/manuscript_package/figures/flattened/*.png` | 10 present, with 9 referenced by the current proof; no alpha channel |

Q1 content final gates rerun on `manuscript_q1.md` / `manuscript_q1.tex`:

| Gate | Path | Result |
|---|---|---|
| Q1 citation check | `08_reviews_revisions/q1_final_citation_check.md` | Pass |
| Q1 result-number check | `08_reviews_revisions/q1_final_result_check.md` | Pass |
| Q1 figure/table check | `08_reviews_revisions/q1_final_figure_table_check.md` | Pass |
| Q1 claim-support check | `08_reviews_revisions/q1_final_claim_support_check.md` | Pass |

Additional Q1 checks:

- PDF page-count queries returned 24 pages for both `manuscript_q1.pdf` and `proofs/manuscript_q1.pdf`.
- `proofs/rendered_pages_q1/` contains 24 page PNGs.
- Focused `manuscript_q1.log` scan found no fatal errors, LaTeX errors, undefined control sequences, undefined references, citation/reference undefined warnings, overfull hboxes, float-too-large errors, missing characters, or rerun cross-reference warnings.
- The Q1 manuscript has 35 references, citation keys resolve to 35 bibitems, and no missing or uncited bibitems were found.
- Jebreel et al. 2026 remains cited as an arXiv preprint; no formal PoPETs DOI or release URL was invented.
- Jälkö et al. 2026 remains cited as an arXiv preprint; no later venue record was assumed.
- Data/Code Availability now points to the Zenodo reproducibility package DOI `https://doi.org/10.5281/zenodo.20552369`.

The preserved near-final v3 package remains a historical checkpoint:

- `09_final/manuscript_package/manuscript_near_final.md`
- `09_final/manuscript_package/proofs/manuscript_near_final.pdf`

The older near-final readiness details below remain valid for that preserved checkpoint, but the active source for subsequent package work is `manuscript_q1.tex`.

## Naming Decision

Do not rename the current near-final package files during this pass.

Rationale:

- `09_final/manuscript_package/` is already a stable package directory.
- `manuscript_near_final.md` and `manuscript_near_final.pdf` accurately describe the current state.
- Renaming these files to `final` before DOI/release fields are real would overstate submission readiness.
- Package filenames contain no spaces, which makes command-line rendering and archiving safer.

Recommended final-release convention after deposit:

- keep the archival release tag stable, for example `v1.0.0`;
- keep the Zenodo DOI stable in manuscript-facing availability text;
- then, if needed for journal upload, create journal-facing copies with venue-specific names while preserving the current package as the traceable near-final proof.

## Required Files Checked

| Item | Path | Result |
|---|---|---|
| Canonical manuscript source | `07_drafts/full_draft_v3.md` | Present |
| Package manuscript source | `09_final/manuscript_package/manuscript_near_final.md` | Present |
| PDF proof | `09_final/manuscript_package/proofs/manuscript_near_final.pdf` | Present |
| Rendered proof pages | `09_final/manuscript_package/proofs/rendered_pages/page-01.png` through `page-27.png` | 27 pages present |
| Data/Code Availability statement | `09_final/data_code_availability_statement.md` | Present |
| Release route plan | `09_final/release_route_and_licence_plan.md` | Present |
| Release licence notes | `09_final/reproducibility_package/release_licence_notes.md` | Present |
| Pinned environment lock | `05_analysis/requirements-lock.txt` | Present |

PDF page count from macOS metadata:

- `kMDItemNumberOfPages = 27`

## Figure and Table Checks

Figure package:

- PNG figures: 4
- SVG vector figures: 4
- PDF vector figures: 4
- Missing SVG exports for PNG figures: none
- Missing vector-PDF exports for PNG figures: none

Main table CSV checks:

| File | Rows | Duplicate columns |
|---|---:|---|
| `table1_dataset_split_summary.csv` | 5 | No |
| `table2_model_comparison.csv` | 25 | No |
| `table3_main_mia_metrics_hardened.csv` | 25 | No |
| `table4_uncertainty_summary.csv` | 3 | No |
| `table5_sample_size_warning_table.csv` | 10 | No |
| `table5b_minimum_nonmember_requirements.csv` | 6 | No |

Appendix table CSV checks:

| File | Rows | Duplicate columns |
|---|---:|---|
| `appendix_table_a1_full_main_metrics.csv` | 500 | No |
| `appendix_table_a2_stage1_confidence_intervals.csv` | 500 | No |
| `appendix_table_a3_hardened_confidence_intervals.csv` | 111 | No |
| `appendix_table_a4_stage1_vs_hardened_ci.csv` | 111 | No |
| `appendix_table_a5_sample_size_sensitivity.csv` | 2,500 | No |
| `appendix_table_a6_sample_size_repeats.csv` | 125,000 | No |
| `appendix_table_a7_sample_size_skipped.csv` | 0 | No |

## Text and Availability Checks

Checked the active Q1 manuscript, arXiv source, and release-facing files for:

- archived-identifier draft markers
- deferred DOI/release-url markers
- `available upon request`
- `for internal review`
- figure draft markers
- `Draft Assembly Notes`
- `Public release still requires`
- `TODO`
- `TBD`
- `FIXME`

Result:

- No blocking draft-marker or deferred-DOI text remains in the active Q1 manuscript or arXiv source.
- Data/Code Availability now cites the Zenodo reproducibility package DOI: `https://doi.org/10.5281/zenodo.20552369`.
- The phrase `available upon request` appears only in author-facing notes saying not to use that wording.

## Submission-Readiness Assessment

Internal Q1 review package:

- Conditional pass.
- The Q1 manuscript source, LaTeX source, PDF proof, figures, tables, appendix tables, Q1 content final gates, release route plan and reproducibility notes are present and consistently named.

External submission package:

- arXiv source-upload pass after Zenodo DOI insertion.
- Remaining external action: publish the Zenodo record before or at the same time as the arXiv version that cites `https://doi.org/10.5281/zenodo.20552369`.
- Target-journal submission still needs venue-specific template, affiliation, email/corresponding-author details, and any journal-specific availability formatting.

Conditional items:

- Repeat the Jebreel et al. 2026 metadata check only if PoPETs 2026 Issue 3 appears before submission.
- Repeat the Jälkö et al. 2026 metadata check before external submission for any arXiv version, venue, or DOI change.
- Add a container recipe only if the public release promises full expanded-grid cross-platform reproduction.

## Next Action

Write the project process summary and final decisions record, then keep the archive manifest aligned with the actual deposit state.
