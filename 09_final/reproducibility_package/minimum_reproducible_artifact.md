# Minimum Reproducible Artifact

Date: 2026-06-05

Status: draft minimum artifact checklist for reviewer use.

Purpose:

- Identify the smallest set of files and commands needed to reproduce the score-array audit reporting layer.
- Separate the fast reporting-layer smoke path from the full expanded empirical reproduction path.

## Minimal Scope

The minimum artifact reproduces the audit-tool reporting layer from supplied member/non-member score arrays. It validates:

- point metrics;
- bootstrap confidence intervals;
- fixed-threshold Wilson intervals;
- repeated balanced subsampling;
- tail-resolution warnings;
- diagnostic figures;
- NPZ and CSV input compatibility.

It does not retrain target models or rerun the full expanded 5 dataset x 5 model grid.

The reviewer package also includes five bounded appendix checks that are larger
than the minimum smoke path but still locally reproducible from existing score
and model artifacts:

- Q1 reference-centered score check for `credit_default` and `adult_income`
  random-forest settings;
- Q1 bounded shadow-model score-array check for the same two random-forest
  settings;
- Q1 tie-rule sensitivity check for representative tied negative-loss rows;
- Q1 split/seed sensitivity check for three representative target
  constructions;
- Q1 label-corruption check for `credit_default` / `random_forest` /
  `neg_loss`.

## Required Files

| File or directory | Purpose |
|---|---|
| `05_analysis/run_audit_tool.py` | Score-array audit CLI. |
| `05_analysis/src/mia_eval/` | Metric, interval, bootstrap, subsampling, plotting, and audit-tool implementation. |
| `05_analysis/examples/make_audit_tool_examples.py` | Generates small NPZ and CSV score-array examples. |
| `05_analysis/examples/example_scores.npz` | NPZ score-array smoke input. |
| `05_analysis/examples/example_scores.csv` | CSV score-array smoke input. |
| `05_analysis/run_q1_stronger_score_appendix.py` | Optional bounded reference-centered score check. |
| `05_analysis/run_q1_lira_like_appendix.py` | Optional bounded shadow-model score-array check. |
| `05_analysis/run_q1_tie_rule_sensitivity.py` | Optional tie-rule sensitivity check. |
| `05_analysis/run_q1_split_seed_sensitivity.py` | Optional split/seed sensitivity check. |
| `05_analysis/run_q1_label_uncertainty_stress.py` | Optional bounded label-corruption check. |
| `05_analysis/requirements.txt` | Python dependencies. |
| `05_analysis/requirements-lock.txt` | Pinned dependency lock used for locked-environment smoke validation. |
| `05_analysis/docs/audit_tool_schema.md` | Input/output schema. |
| `05_analysis/docs/audit_tool_interpretation_guide.md` | Reader-facing interpretation guide. |
| `09_final/reproducibility_package/smoke_reproduction.md` | Fast smoke commands. |
| `09_final/reproducibility_package/clean_env_smoke.md` | Clean-environment smoke validation record. |

## Minimal Commands

Run from the project root:

```bash
python3 -m pip install -r 05_analysis/requirements-lock.txt
python3 05_analysis/examples/make_audit_tool_examples.py
```

NPZ smoke:

```bash
python3 05_analysis/run_audit_tool.py \
  --input 05_analysis/examples/example_scores.npz \
  --input-format npz \
  --output-dir 05_analysis/results/audit_tool_example_npz \
  --dataset credit_default \
  --model random_forest \
  --n-bootstrap 25 \
  --n-repeats 10 \
  --sample-sizes 250 500 \
  --random-state 20260603
```

CSV smoke:

```bash
python3 05_analysis/run_audit_tool.py \
  --input 05_analysis/examples/example_scores.csv \
  --input-format csv \
  --output-dir 05_analysis/results/audit_tool_example_csv \
  --score-names neg_loss confidence neg_entropy modified_entropy \
  --membership-column membership \
  --dataset credit_default \
  --model random_forest \
  --n-bootstrap 25 \
  --n-repeats 10 \
  --sample-sizes 250 500 \
  --random-state 20260603
```

## Expected Outputs

Each smoke run should produce:

- `run_config.json`
- `run_summary.md`
- `metrics/main_metrics.csv`
- `metrics/confidence_intervals.csv`
- `metrics/fixed_threshold_intervals.csv`
- `subsampling/sample_size_repeats.csv`
- `subsampling/sample_size_sensitivity.csv`
- `subsampling/sample_size_skipped.csv`
- `diagnostics/tail_resolution_warnings.csv`
- `figures/low_fpr_roc.png`
- `figures/score_distribution_<score>.png`
- `figures/tpr_at_fpr_vs_audit_size.png`
- `figures/interval_width_vs_audit_size.png`

The current clean-environment smoke test confirmed that NPZ and CSV AUC snapshots match for the generated example scores.

## Optional Reviewer Appendix Checks

These checks are not required for the minimum smoke path, but they are part of
the reviewer-facing reproducibility package.

Reference-centered score check:

```bash
python3 05_analysis/run_q1_stronger_score_appendix.py \
  --dataset credit_default \
  --model random_forest \
  --target-model-subdir expanded_tabular_stage1/models \
  --baseline-score-subdir expanded_tabular_stage1/attack_scores \
  --output-dir 05_analysis/results/q1_stronger_score_appendix/credit_default_random_forest \
  --n-reference-models 12 \
  --reference-n-estimators 100 \
  --reference-train-fraction 0.5 \
  --min-holdout-references 3 \
  --min-reference-std 1e-6 \
  --random-state 20260602 \
  --n-jobs -1 \
  --max-iter 1000
```

Then run:

```bash
python3 05_analysis/run_audit_tool.py \
  --input 05_analysis/results/q1_stronger_score_appendix/credit_default_random_forest/score_arrays/stronger_scores.npz \
  --input-format npz \
  --output-dir 05_analysis/results/q1_stronger_score_appendix/credit_default_random_forest/audit_tool \
  --score-names ref_centered_neg_loss ref_logit_margin ref_z_logit_margin \
  --dataset credit_default \
  --model random_forest_reference_centered \
  --n-bootstrap 1000 \
  --n-repeats 200 \
  --sample-sizes 250 500 1000 2500 5000 10000 \
  --random-state 20260602
```

Expected key row counts: `comparison_metrics.csv` has 12 rows,
`audit_tool/metrics/main_metrics.csv` has 15 rows, and
`audit_tool/subsampling/sample_size_repeats.csv` has 18,000 rows.

Additional bounded appendix checks:

The bounded shadow-model, tie-rule, split/seed, and label-corruption checks are
documented in `commands.md` with exact parameters, seeds, output paths, and row
counts. The minimum smoke artifact does not require running them, but they are
part of the reviewer-facing Q1 appendix evidence.

Label-corruption check:

```bash
python3 05_analysis/run_q1_label_uncertainty_stress.py \
  --dataset credit_default \
  --model random_forest \
  --score-name neg_loss \
  --attack-score-subdir expanded_tabular_stage1/attack_scores \
  --output-dir 05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss \
  --corruption-rates 0 0.005 0.01 0.02 0.05 \
  --n-repeats 200 \
  --sample-sizes 250 500 1000 2500 5000 10000 15000 \
  --random-state 20260602
```

Then run the canonical audit-tool pass:

```bash
for slug in 0p000 0p005 0p010 0p020 0p050; do
  python3 05_analysis/run_audit_tool.py \
    --input "05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/score_arrays/neg_loss_label_corruption_${slug}.npz" \
    --input-format npz \
    --output-dir "05_analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_${slug}" \
    --score-names neg_loss \
    --dataset credit_default \
    --model "random_forest_neg_loss_label_corruption_${slug}" \
    --n-bootstrap 1000 \
    --n-repeats 200 \
    --sample-sizes 250 500 1000 2500 5000 10000 \
    --random-state 20260602 \
    --skip-figures
done
```

Expected key row counts: `label_uncertainty_repeats.csv` has 5,000 rows,
`label_uncertainty_summary.csv` has 25 rows,
`canonical_corruption_metrics.csv` has 25 rows, and each
`audit_tool/corruption_<slug>/subsampling/sample_size_repeats.csv` has 6,000
rows.

## Full Empirical Reproduction Boundary

The full empirical study additionally requires:

- public raw datasets under `03_data_raw/`;
- cleaned datasets and split files under `04_data_cleaned/`;
- `05_analysis/run_experiment.py` for the expanded 5 dataset x 5 model grid;
- `05_analysis/run_final_ci_hardening.py` for selected 1,000-bootstrap intervals;
- figure and table generation scripts.

Those commands are documented in `commands.md` and `data_and_outputs_manifest.md`. They are not part of the minimum audit-tool smoke path.

## Public Release Boundary

- The current minimum artifact has passed a clean temporary virtual-environment smoke test.
- A pinned requirements lock exists at `05_analysis/requirements-lock.txt`.
- The pinned lock has passed the audit-tool smoke validation recorded in `09_final/reproducibility_package/locked_env_smoke.md`.
- The public DOI/release URL remains pending actual deposit, but the reviewer
  package can be locally reproduced from the documented commands and expected
  row counts.
- Before public archival release, add repository DOI/release URL and licence details. A container recipe remains optional if stronger cross-platform reproducibility is required.
