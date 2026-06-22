# 05 Analysis Results

Purpose: generated experiment outputs, validation outputs, audit-tool outputs,
and manuscript-facing result snapshots.

Largest folders:
- `expanded_tabular_stage1/`: full expanded 5 dataset x 5 model first-pass grid.
- `core/`: original core experiment outputs for `credit_default` and `covertype`.

Manuscript-critical folders:
- `expanded_tabular_stage1/`: full stage1 evidence base.
- `final_ci_hardening/`: selected 1000-bootstrap hardened interval rows.
- `q1_stronger_score_appendix/`: stronger-score compatibility appendix evidence.
- `q1_label_uncertainty_stress/`: bounded audit-label uncertainty stress test.
- `lock_env_smoke_npz/` and `lock_env_smoke_csv/`: pinned-lock audit-tool smoke outputs.

Validation and smoke folders:
- `runner_smoke/`
- `models_smoke/`
- `attack_scores_smoke/`
- `metrics_smoke/`
- `subsampling_smoke/`
- `expanded_smoke/`
- `audit_tool_npz_smoke/`
- `audit_tool_example_npz/`
- `audit_tool_example_csv/`
- `clean_env_smoke_npz/`
- `clean_env_smoke_csv/`
- `final_ci_hardening_smoke/`
- `final_ci_hardening_smoke_fast/`

Model-extension and review-support folders:
- `model_extension_hgb/`
- `extratrees_sanity_check/`

Do not delete result folders unless the corresponding manuscript/check record is
also updated. Many files in `process_record/`, `08_reviews_revisions/`, and
`release/` cite these paths as evidence.
