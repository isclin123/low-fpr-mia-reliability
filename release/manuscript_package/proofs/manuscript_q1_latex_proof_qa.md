# Q1 LaTeX Proof QA

Date: 2026-06-05

Status: final arXiv-ready internal proof candidate after the 2026-06-05 multi-review novelty, method-boundary, layout hardening, supplemental-completion, and final table/appendix-figure layout pass. The manuscript is in a compact two-column, PoPETs/ACM-like style with bracket numeric citations, Appendix A-J, six main-text figures plus three appendix diagnostic figures, 35 references, and a 24-page rendered PDF.

## Source and Outputs

| Artifact | Path |
|---|---|
| Synchronized Markdown reading copy | `release/manuscript_package/manuscript_q1.md` |
| Authoritative LaTeX source | `release/manuscript_package/manuscript_q1.tex` |
| Compiled PDF | `release/manuscript_package/manuscript_q1.pdf` |
| Rendered page proofs | `release/manuscript_package/proofs/rendered_pages_q1/page-*.png` |
| Contact sheet | `release/manuscript_package/proofs/manuscript_q1_contact_sheet.png` |
| arXiv source folder | `release/manuscript_package/arxiv_upload/` |
| arXiv upload zip | `release/manuscript_package/arxiv_upload.zip` |

## Build Commands

From `release/manuscript_package/`:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error manuscript_q1.tex
cp manuscript_q1.pdf proofs/manuscript_q1.pdf
rm -rf proofs/rendered_pages_q1
mkdir -p proofs/rendered_pages_q1
pdftoppm -r 144 -png proofs/manuscript_q1.pdf proofs/rendered_pages_q1/page
```

The arXiv package was refreshed after the 2026-06-05 supplemental-completion and final layout pass by copying `manuscript_q1.tex` to `arxiv_upload/main.tex`, compiling `main.tex` in `arxiv_upload/build/`, and zipping only `main.tex` plus `figures/`. The rebuilt zip was also extracted to a temporary directory and compiled independently.

## Final Checks

- Root PDF page count: 24.
- Rendered proof PNG count: 24.
- arXiv build PDF page count: 24.
- arXiv zip extraction compile page count: 24.
- `latexmk -xelatex` completed for both the root proof and `arxiv_upload/main.tex`.
- Log keyword check found no fatal error, undefined reference, citation warning, float-too-large warning, overfull hbox/vbox warning, missing-character warning, or remaining label-rerun warning.
- Root and arXiv PDF text extraction matched exactly.
- Source scan found no remaining legacy compatibility wording in the active manuscript/arXiv source or Q1 figure generator.
- PDF text extraction found no visible local user paths, project-stage folders, CSV/NPZ/JSON/Markdown filenames, figure source paths, or `Source file` notes.
- Source residual scan found no visible `stage1`, `hardened`, local file/path, draft-marker, or audit-tool run wording; LaTeX figure paths remain only as required source references.

## Visual QA

- Rendered-page review found no blank pages and no table clipping or overlap.
- Page 1 was rechecked after the abstract percent-sign repair; the abstract is complete and not truncated.
- Pages 11-13 were rechecked after the Table 3/Figure 4/Figure 5 revision; Table 3 is readable, Figure 4 shows TPR@0.1%FPR audit-size uncertainty, and the supplemental-check boundary prose is no longer split by a list/floating figure.
- Page 5 formula blocks were checked for centering, line breaks, and alignment.
- Page 11 checklist table is now a formal full-width table rather than a loose Box-style list.
- Page 17 references use bracket numeric labels and no Nature-style bare numbered list.
- Pages 21-24 show Appendix A-J with compact printed data tables and added Appendix H/I/J diagnostic figures; the final appendix material remains bounded and readable.
- Header draft-marker text was removed; the running header now uses `Yi` only.
- The Jälkö et al. 2026 reference, added adjacent novelty-boundary references, novelty framing, and Appendix F reference-centered score wording were checked after recompilation.

## Current Boundary

This QA validates rendered layout and arXiv-package compilation for the current manuscript package. It does not validate future external-submission metadata such as a final DOI, code-release DOI, licence text, or journal-specific submission forms.
