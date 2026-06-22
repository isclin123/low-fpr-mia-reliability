# Q1 Completion and arXiv-Ready Record

Date: 2026-06-05

## Completed previously open items

- Integrated a bounded shadow-model score-array check into the manuscript as Appendix H.
  - Script: `analysis/run_q1_lira_like_appendix.py`
  - Outputs: `analysis/results/q1_lira_like_appendix/`
  - Scope: global pooled shadow train/holdout Gaussian likelihood-ratio-style score, not a full LiRA/RMIA benchmark.
- Integrated tie-rule sensitivity as Appendix I.
  - Script: `analysis/run_q1_tie_rule_sensitivity.py`
  - Outputs: `analysis/results/q1_tie_rule_sensitivity/`
  - Scope: strict, randomized tie-aware, and inclusive threshold rules for representative negative-loss rows.
- Added and ran split/seed sensitivity as Appendix J.
  - Script: `analysis/run_q1_split_seed_sensitivity.py`
  - Outputs: `analysis/results/q1_split_seed_sensitivity/`
  - Scope: five repeated stratified split/model seeds for CD/RF, CD/ET, and Adult/RF negative-loss rows.
- Updated Methods, Results, Discussion, Limitations, Future Work, Conclusion, Data/Code Availability, Appendix B output index, and the reproducibility package so the new evidence is not appendix-only.
- Completed a final layout pass after PDF review:
  - fixed the Table 1/Table 2 ordering by replacing the wide Table 1 float with an inline single-column table;
  - converted the former unnumbered "Representative gap/AUC rows" block into a captioned main-text table;
  - added Appendix H/I/J diagnostic figures generated from existing CSV outputs.
- Regenerated `release/manuscript_package/manuscript_q1.md` from the current TeX source as a synchronized reading copy. The authoritative source remains `manuscript_q1.tex`.
- Added the Zenodo reproducibility-package DOI to the manuscript Data and Code Availability section, release notes, and package metadata:
  - `https://doi.org/10.5281/zenodo.20552369`
  - The Zenodo record must be published before or at the same time as the public arXiv version that cites this DOI.

## Verification

- Python compile check passed for:
  - `analysis/generate_expanded_outputs.py`
  - `analysis/generate_final_tables.py`
  - `analysis/run_q1_stronger_score_appendix.py`
  - `analysis/run_q1_lira_like_appendix.py`
  - `analysis/run_q1_tie_rule_sensitivity.py`
  - `analysis/run_q1_split_seed_sensitivity.py`
  - `analysis/run_q1_label_uncertainty_stress.py`
- Main manuscript compiled with:
  - `latexmk -xelatex -interaction=nonstopmode -halt-on-error manuscript_q1.tex`
- arXiv source directory compiled with:
  - `latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex`
- The final manuscript PDF is 24 pages, letter size.
- Final log scan found no fatal errors, undefined references/citations, overfull boxes, or missing-character warnings.
- Cite/bibitem closure check:
  - 35 cite keys
  - 35 bibitems
  - 0 missing bibitems
  - 0 uncited bibitems
- New Q1 table row-count checks passed:
  - bounded shadow key metrics: 4 rows
  - shadow fit summary: 2 rows
  - shadow model runs: 16 rows
  - tie-rule long rows: 24 rows
  - tie-rule paper table: 8 rows
  - split/seed metric rows: 45 rows
  - split/seed summary rows: 9 rows
  - split/seed paper table: 3 rows
- Appendix pages 21--24 were rendered to PNG and visually checked for table clipping, overlap, missing glyphs, and black blocks.
- `arxiv_upload.zip` passed `zip -T`.
- `arxiv_upload.zip` contains only `main.tex` and the required `figures/flattened/*.png` assets, 13 zip entries total.
- `arxiv_upload.zip` was extracted into `/tmp/mia_arxiv_upload_check` and compiled successfully with `latexmk -xelatex`.

## Upload note

Upload only:

- `release/manuscript_package/arxiv_upload.zip`

Do not upload the whole `release/manuscript_package/` directory.

## Remaining external-only item

The DOI is now reserved and inserted. The remaining external-only action is to publish the Zenodo record containing `release/zenodo_release/mia_low_fpr_reliability_reproducibility_v1.0.0.zip` before or at the same time as the arXiv version that cites `https://doi.org/10.5281/zenodo.20552369`.
