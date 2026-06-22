# Data and Outputs Manifest

Date: 2026-06-05

## Data Provenance

Primary provenance file:

- `data_sources/data_sources.md`

Preprocessing record:

- `data_processed/preprocessing_log.md`

Cleaned dataset records:

| Dataset | Cleaned metadata | Data dictionary |
|---|---|---|
| credit_default | `data_processed/credit_default/metadata.json` | `data_processed/credit_default/data_dictionary.md` |
| covertype | `data_processed/covertype/metadata.json` | `data_processed/covertype/data_dictionary.md` |
| adult_income | `data_processed/adult_income/metadata.json` | `data_processed/adult_income/data_dictionary.md` |
| bank_marketing | `data_processed/bank_marketing/metadata.json` | `data_processed/bank_marketing/data_dictionary.md` |
| diabetes_readmission | `data_processed/diabetes_readmission/metadata.json` | `data_processed/diabetes_readmission/data_dictionary.md` |

Split policy:

- 50/50 member/non-member split.
- Stratified by target label.
- Random state: `20260602`.

## Configuration and Scripts

| Artifact | Purpose |
|---|---|
| `analysis/configs/expanded_tabular_v1.json` | Expanded run scope and completed-status config. |
| `analysis/run_experiment.py` | End-to-end dataset/model/score/metric/subsampling runner. |
| `analysis/run_audit_tool.py` | Reusable score-array audit CLI. |
| `analysis/run_final_ci_hardening.py` | Selected 1,000-bootstrap final CI hardening. |
| `analysis/run_q1_stronger_score_appendix.py` | Bounded reference-centered score compatibility check for the Q1 appendix. |
| `analysis/run_q1_lira_like_appendix.py` | Bounded shadow-model score-array compatibility check for the Q1 appendix. |
| `analysis/run_q1_tie_rule_sensitivity.py` | Strict/randomized/inclusive low-FPR tie-rule sensitivity check. |
| `analysis/run_q1_split_seed_sensitivity.py` | Bounded split/seed sensitivity check for representative target constructions. |
| `analysis/run_q1_label_uncertainty_stress.py` | Bounded label-corruption check for the Q1 appendix. |
| `analysis/generate_expanded_outputs.py` | Expanded figures and summary table generation. |
| `analysis/generate_final_tables.py` | Final main and appendix table generation. |
| `analysis/requirements-lock.txt` | Pinned dependency lock for the audit-tool smoke release path. |

## Main Result Directories

| Directory | Contents | Status |
|---|---|---|
| `analysis/results/expanded_tabular_stage1/` | Full five-dataset/five-model stage1 outputs with 50 bootstrap repeats and 50 subsampling repeats. | Complete. |
| `analysis/results/final_ci_hardening/` | Selected 1,000-bootstrap hardened intervals for main-table candidate rows. | Complete. |
| `analysis/results/audit_tool_example_npz/` | NPZ audit-tool example output. | Complete smoke/example validation. |
| `analysis/results/audit_tool_example_csv/` | CSV audit-tool example output. | Complete smoke/example validation. |
| `analysis/results/clean_env_smoke_npz/` | NPZ audit-tool example output from the clean virtual-environment smoke test. | Complete clean-env smoke validation. |
| `analysis/results/clean_env_smoke_csv/` | CSV audit-tool example output from the clean virtual-environment smoke test. | Complete clean-env smoke validation. |
| `analysis/results/lock_env_smoke_npz/` | NPZ audit-tool example output from the pinned-lock clean virtual-environment smoke test. | Complete locked-env smoke validation. |
| `analysis/results/lock_env_smoke_csv/` | CSV audit-tool example output from the pinned-lock clean virtual-environment smoke test. | Complete locked-env smoke validation. |
| `analysis/results/lock_env_smoke_freeze.txt` | Package freeze observed inside the pinned-lock smoke environment. | Complete locked-env smoke validation. |
| `analysis/results/q1_stronger_score_appendix/credit_default_random_forest/` | Reference-centered score arrays, baseline comparison metrics, and audit-tool outputs for the Q1 score check. | Complete bounded Q1 appendix check. |
| `analysis/results/q1_stronger_score_appendix/adult_income_random_forest/` | Adult Income reference-centered score arrays, baseline comparison metrics, and audit-tool outputs for the Q1 score check. | Complete bounded Q1 appendix check. |
| `analysis/results/q1_lira_like_appendix/` | Bounded shadow-model score arrays, shadow-fit summaries, key metrics, and audit-tool outputs. | Complete bounded Q1 appendix check. |
| `analysis/results/q1_tie_rule_sensitivity/` | Strict/randomized/inclusive low-FPR tie-rule operating-point tables. | Complete bounded Q1 sensitivity check. |
| `analysis/results/q1_split_seed_sensitivity/` | Repeated target-construction split/seed metric rows and summaries. | Complete bounded Q1 sensitivity check. |
| `analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/` | Label-corruption repeat metrics, canonical corrupted score arrays, and canonical audit-tool outputs. | Complete bounded Q1 check. |
| `figures_tables/expanded/` | Expanded figures and model-comparison summary. | Regenerated with PNG/SVG/PDF figure exports. |
| `figures_tables/final_tables/` | Final main manuscript table package. | Complete. |
| `figures_tables/appendix_tables/` | Appendix metric, CI, and subsampling tables. | Complete. |

## Expected Output Counts

| Output | Expected rows |
|---|---:|
| `expanded_tabular_stage1/metrics/main_metrics.csv` | 500 |
| `expanded_tabular_stage1/metrics/confidence_intervals.csv` | 500 |
| `expanded_tabular_stage1/subsampling/sample_size_repeats.csv` | 125,000 |
| `expanded_tabular_stage1/subsampling/sample_size_sensitivity.csv` | 2,500 |
| `final_ci_hardening/hardened_confidence_intervals.csv` | 111 |
| `final_tables/table3_main_mia_metrics_hardened.csv` | 25 |
| `appendix_tables/appendix_table_a1_full_main_metrics.csv` | 500 |
| `appendix_tables/appendix_table_a2_stage1_confidence_intervals.csv` | 500 |
| `appendix_tables/appendix_table_a5_sample_size_sensitivity.csv` | 2,500 |
| `appendix_tables/appendix_table_a6_sample_size_repeats.csv` | 125,000 |
| `q1_stronger_score_appendix/credit_default_random_forest/score_arrays/score_summary.csv` | 6 |
| `q1_stronger_score_appendix/credit_default_random_forest/score_arrays/reference_model_diagnostics.csv` | 12 |
| `q1_stronger_score_appendix/credit_default_random_forest/comparison_metrics.csv` | 12 |
| `q1_stronger_score_appendix/credit_default_random_forest/audit_tool/metrics/main_metrics.csv` | 15 |
| `q1_stronger_score_appendix/credit_default_random_forest/audit_tool/metrics/confidence_intervals.csv` | 15 |
| `q1_stronger_score_appendix/credit_default_random_forest/audit_tool/metrics/fixed_threshold_intervals.csv` | 12 |
| `q1_stronger_score_appendix/credit_default_random_forest/audit_tool/subsampling/sample_size_repeats.csv` | 18,000 |
| `q1_stronger_score_appendix/credit_default_random_forest/audit_tool/subsampling/sample_size_sensitivity.csv` | 90 |
| `q1_stronger_score_appendix/credit_default_random_forest/audit_tool/diagnostics/tail_resolution_warnings.csv` | 42 |
| `q1_lira_like_appendix/tables/key_metrics.csv` | 4 |
| `q1_lira_like_appendix/tables/shadow_fit_summary.csv` | 2 |
| `q1_lira_like_appendix/tables/shadow_model_runs.csv` | 16 |
| each `q1_lira_like_appendix/audit_tool/.../metrics/main_metrics.csv` | 5 |
| each `q1_lira_like_appendix/audit_tool/.../metrics/confidence_intervals.csv` | 5 |
| each `q1_lira_like_appendix/audit_tool/.../metrics/fixed_threshold_intervals.csv` | 4 |
| each `q1_lira_like_appendix/audit_tool/.../subsampling/sample_size_repeats.csv` | 6,000 |
| each `q1_lira_like_appendix/audit_tool/.../subsampling/sample_size_sensitivity.csv` | 30 |
| each `q1_lira_like_appendix/audit_tool/.../diagnostics/tail_resolution_warnings.csv` | 16 |
| `q1_tie_rule_sensitivity/tie_rule_operating_points.csv` | 24 |
| `q1_tie_rule_sensitivity/paper_table_tie_rule_sensitivity.csv` | 8 |
| `q1_split_seed_sensitivity/split_seed_metric_rows.csv` | 45 |
| `q1_split_seed_sensitivity/split_seed_summary.csv` | 9 |
| `q1_split_seed_sensitivity/paper_table_split_seed_sensitivity.csv` | 3 |
| `q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/label_uncertainty_repeats.csv` | 5,000 |
| `q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/label_uncertainty_summary.csv` | 25 |
| `q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/canonical_corruption_metrics.csv` | 25 |
| `q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/canonical_score_arrays.csv` | 5 |
| `q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/tail_resolution_warnings.csv` | 70 |
| each `q1_label_uncertainty_stress/.../audit_tool/corruption_<slug>/metrics/main_metrics.csv` | 5 |
| each `q1_label_uncertainty_stress/.../audit_tool/corruption_<slug>/metrics/confidence_intervals.csv` | 5 |
| each `q1_label_uncertainty_stress/.../audit_tool/corruption_<slug>/metrics/fixed_threshold_intervals.csv` | 4 |
| each `q1_label_uncertainty_stress/.../audit_tool/corruption_<slug>/subsampling/sample_size_repeats.csv` | 6,000 |
| each `q1_label_uncertainty_stress/.../audit_tool/corruption_<slug>/subsampling/sample_size_sensitivity.csv` | 30 |
| each `q1_label_uncertainty_stress/.../audit_tool/corruption_<slug>/diagnostics/tail_resolution_warnings.csv` | 14 |

Q1 reference-centered score arrays contain 15,000 members and 15,000
nonmembers for Credit Default and 24,421 members and 24,421 nonmembers for
Adult Income for each of `ref_centered_neg_loss`, `ref_logit_margin`, and
`ref_z_logit_margin`. Q1 bounded shadow-model arrays contain the same
member/nonmember counts for `shadow_lira_like_neg_loss`; the name is historical
and the manuscript treats the check as a bounded shadow-model score-array
compatibility case, not a full LiRA/RMIA benchmark. Q1 label-corruption
canonical arrays contain 15,000 observed members and 15,000 observed nonmembers
for each corruption slug
`0p000`, `0p005`, `0p010`, `0p020`, and `0p050`.

## Validity and QA Records

| Record | Purpose |
|---|---|
| `process_record/expanded_run_validity_report.md` | Expanded stage1 completeness, bug fix, and output-count validation. |
| `process_record/final_ci_hardening_report.md` | Scope and validation of selected final CI hardening. |
| `08_reviews_revisions/figure_table_qa_good_paper.md` | Figure/table source traceability and export QA. |
| `07_drafts/uncertainty_methods_note.md` | Distinguishes bootstrap, Wilson, subsampling, and tail-warning interpretations. |
| `analysis/docs/audit_tool_interpretation_guide.md` | Reader-facing guide to audit-tool outputs. |
| `release/reproducibility_package/clean_env_smoke.md` | Clean virtual-environment smoke-test record for the audit-tool examples. |
| `release/reproducibility_package/locked_env_smoke.md` | Pinned-lock clean virtual-environment smoke-test record for the audit-tool examples. |
| `release/reproducibility_package/minimum_reproducible_artifact.md` | Smallest reviewer-facing artifact path for the score-array reporting layer. |

## Release and Large Artifact Note

This package is a reproducibility draft. The public DOI/release URL is still
pending actual deposit, but the reviewer package is locally reproducible from
the documented commands, seeds, parameters, expected row counts, and output
paths. For external release, raw third-party datasets should be cited through
UCI/scikit-learn rather than redistributed by default. Processed/split arrays
and generated manuscript artifacts should be deposited where upstream terms
permit redistribution. Large generated outputs, especially the expanded-stage
result directory, should be hosted in Zenodo or regenerated from the documented
commands and expected output counts rather than committed to the Git repository.

Release-route and licence/reuse details are recorded in `release/release_route_and_licence_plan.md` and `release/reproducibility_package/release_licence_notes.md`.
