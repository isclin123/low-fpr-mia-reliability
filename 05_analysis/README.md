# 05 Analysis

Purpose: experiment scripts, run configs, metric tables, and analysis logs.

Current status:
- Reusable pipeline exists for data loading, model training, attack-score extraction, metrics, bootstrap intervals, fixed-threshold intervals, and sample-size sensitivity.
- The score-array audit tool exists in `src/mia_eval/audit_tool.py` with CLI entry point `run_audit_tool.py`.
- Expanded tabular stage1 results, final CI hardening, reproducibility smoke tests, and Q1 strengthening outputs are present under `results/`.
- The result directory is intentionally large. The largest folders are `expanded_tabular_stage1/` and `core/`.

Main entry points:
- Run full experiments: `run_experiment.py`
- Run score-array audit tool: `run_audit_tool.py`
- Generate expanded figures/tables: `generate_expanded_outputs.py`
- Generate final manuscript tables: `generate_final_tables.py`
- Final CI hardening: `run_final_ci_hardening.py`
- Q1 stronger-score appendix: `run_q1_stronger_score_appendix.py`
- Q1 label-uncertainty stress test: `run_q1_label_uncertainty_stress.py`

Important code:
- `src/mia_eval/data.py`
- `src/mia_eval/models.py`
- `src/mia_eval/attacks.py`
- `src/mia_eval/experiments.py`
- `src/mia_eval/audit_tool.py`
- `src/mia_eval/intervals.py`
- `src/mia_eval/subsampling.py`

Indexes:
- Results map: `results/README.md`
- Audit-tool schema: `docs/audit_tool_schema.md`
- Audit-tool interpretation guide: `docs/audit_tool_interpretation_guide.md`

Optional R usage:
- R/RStudio can be used for supplementary statistical checks, plotting, or manuscript-support analysis.
- Keep the core reproducible experiment pipeline in Python unless there is a specific reason to bridge languages.
