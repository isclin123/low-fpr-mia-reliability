# Reproduction Commands

Date: 2026-06-05

Run all commands from the project root:

```bash
cd /path/to/MIA
```

Replace `/path/to/MIA` with the cloned project root.

## 1. Install Dependencies

```bash
python3 -m pip install -r analysis/requirements.txt
```

For the public-release smoke path, prefer the pinned lock:

```bash
python3 -m pip install -r analysis/requirements-lock.txt
```

Optional:

```bash
export PYTHONPATH="$PWD/analysis/src:$PYTHONPATH"
```

## 2. Fast Audit-Tool Smoke Path

Regenerate example score files:

```bash
python3 analysis/examples/make_audit_tool_examples.py
```

Run the NPZ example:

```bash
python3 analysis/run_audit_tool.py \
  --input analysis/examples/example_scores.npz \
  --input-format npz \
  --output-dir analysis/results/audit_tool_example_npz \
  --dataset credit_default \
  --model random_forest \
  --n-bootstrap 25 \
  --n-repeats 10 \
  --sample-sizes 250 500 \
  --random-state 20260603
```

Run the CSV example:

```bash
python3 analysis/run_audit_tool.py \
  --input analysis/examples/example_scores.csv \
  --input-format csv \
  --output-dir analysis/results/audit_tool_example_csv \
  --score-names neg_loss confidence neg_entropy modified_entropy \
  --membership-column membership \
  --dataset credit_default \
  --model random_forest \
  --n-bootstrap 25 \
  --n-repeats 10 \
  --sample-sizes 250 500 \
  --random-state 20260603
```

## 3. Full Expanded Tabular Stage1 Run

This is the full 5 dataset x 5 model grid. It can take substantially longer than the smoke path.

```bash
python3 analysis/run_experiment.py \
  --run-name expanded_tabular_stage1 \
  --datasets credit_default covertype adult_income bank_marketing diabetes_readmission \
  --models logistic_regression random_forest hist_gradient_boosting extra_trees small_mlp \
  --prepare-data \
  --random-state 20260602 \
  --n-bootstrap 50 \
  --n-repeats 50 \
  --sample-sizes 250 500 1000 2000 5000
```

If trained models already exist and only score/metric/subsampling outputs need regeneration:

```bash
python3 analysis/run_experiment.py \
  --run-name expanded_tabular_stage1 \
  --datasets credit_default covertype adult_income bank_marketing diabetes_readmission \
  --models logistic_regression random_forest hist_gradient_boosting extra_trees small_mlp \
  --skip-train \
  --random-state 20260602 \
  --n-bootstrap 50 \
  --n-repeats 50 \
  --sample-sizes 250 500 1000 2000 5000
```

Expected main outputs:

- `analysis/results/expanded_tabular_stage1/metrics/main_metrics.csv`
- `analysis/results/expanded_tabular_stage1/metrics/confidence_intervals.csv`
- `analysis/results/expanded_tabular_stage1/subsampling/sample_size_sensitivity.csv`
- `analysis/results/expanded_tabular_stage1/subsampling/sample_size_repeats.csv`

## 4. Expanded Figures and Sample-Size Requirements

```bash
python3 analysis/generate_expanded_outputs.py
```

Expected outputs:

- `figures_tables/expanded/expanded_best_auc_heatmap.{png,svg,pdf}`
- `figures_tables/expanded/expanded_neg_loss_low_fpr_heatmaps.{png,svg,pdf}`
- `figures_tables/expanded/expanded_accuracy_gap_vs_best_auc.{png,svg,pdf}`
- `figures_tables/expanded/expanded_auc_width_by_audit_size.{png,svg,pdf}`
- `figures_tables/expanded/expanded_model_comparison_summary.csv`
- `analysis/results/expanded_tabular_stage1/sample_size_requirements.md`

## 5. Selected Final CI Hardening

```bash
python3 analysis/run_final_ci_hardening.py \
  --source-run-name expanded_tabular_stage1 \
  --attack-score-subdir expanded_tabular_stage1/attack_scores \
  --summary-csv figures_tables/expanded/expanded_model_comparison_summary.csv \
  --stage1-ci-csv analysis/results/expanded_tabular_stage1/metrics/confidence_intervals.csv \
  --output-dir analysis/results/final_ci_hardening \
  --n-bootstrap 1000 \
  --confidence 0.95 \
  --random-state 20260603
```

Expected outputs:

- `analysis/results/final_ci_hardening/selected_score_rows.csv`
- `analysis/results/final_ci_hardening/hardened_confidence_intervals.csv`
- `analysis/results/final_ci_hardening/stage1_vs_hardened_confidence_intervals.csv`
- `analysis/results/final_ci_hardening/hardening_summary.md`

## 6. Final Main and Appendix Tables

```bash
python3 analysis/generate_final_tables.py
```

Expected outputs:

- `figures_tables/final_tables/`
- `figures_tables/appendix_tables/`

## 7. Q1 Reference-Centered Score Compatibility Check

This bounded compatibility check uses the `credit_default` / `random_forest`
and `adult_income` / `random_forest` target models from
`expanded_tabular_stage1`, trains 12 reference models per setting, and then
runs the audit tool on three reference-centered scores. It is a
reference-centered score workflow-reuse check, not a LiRA/RMIA benchmark. The
script name keeps the historical `stronger_score` label, but the manuscript
reports this as a reference-centered compatibility check.

Generate the reference-centered score arrays and run the audit-tool reporting
layer:

```bash
for dataset in credit_default adult_income; do
  out="analysis/results/q1_stronger_score_appendix/${dataset}_random_forest"

  python3 analysis/run_q1_stronger_score_appendix.py \
    --dataset "$dataset" \
    --model random_forest \
    --target-model-subdir expanded_tabular_stage1/models \
    --baseline-score-subdir expanded_tabular_stage1/attack_scores \
    --output-dir "$out" \
    --n-reference-models 12 \
    --reference-n-estimators 100 \
    --reference-train-fraction 0.5 \
    --min-holdout-references 3 \
    --min-reference-std 1e-6 \
    --random-state 20260602 \
    --n-jobs -1 \
    --max-iter 1000

  python3 analysis/run_audit_tool.py \
    --input "$out/score_arrays/stronger_scores.npz" \
    --input-format npz \
    --output-dir "$out/audit_tool" \
    --score-names ref_centered_neg_loss ref_logit_margin ref_z_logit_margin \
    --dataset "$dataset" \
    --model random_forest_reference_centered \
    --n-bootstrap 1000 \
    --n-repeats 200 \
    --sample-sizes 250 500 1000 2500 5000 10000 \
    --random-state 20260602
done
```

Expected outputs and row counts:

- `credit_default_random_forest/score_arrays/stronger_scores.npz`: 15,000 members and 15,000 nonmembers per reference-centered score.
- `adult_income_random_forest/score_arrays/stronger_scores.npz`: 24,421 members and 24,421 nonmembers per reference-centered score.
- For each setting: `score_summary.csv` has 6 rows; `reference_model_diagnostics.csv` has 12 rows; `comparison_metrics.csv` has 12 rows.
- For each setting's `audit_tool/`: `main_metrics.csv` has 15 rows; `confidence_intervals.csv` has 15 rows; `fixed_threshold_intervals.csv` has 12 rows; `sample_size_repeats.csv` has 18,000 rows; `sample_size_sensitivity.csv` has 90 rows; `tail_resolution_warnings.csv` has 42 rows; `sample_size_skipped.csv` has 0 rows.

## 8. Q1 Bounded Shadow-Model Score-Array Check

This bounded check generates a global shadow-model likelihood-ratio-style score
array for `credit_default` / `random_forest` and `adult_income` /
`random_forest`. It is a shadow-model score-array compatibility case, not a
full LiRA/RMIA benchmark.

```bash
python3 analysis/run_q1_lira_like_appendix.py \
  --datasets credit_default adult_income \
  --model random_forest \
  --attack-score-subdir expanded_tabular_stage1/attack_scores \
  --output-dir analysis/results/q1_lira_like_appendix \
  --n-shadows 8 \
  --n-estimators 80 \
  --n-bootstrap 1000 \
  --n-repeats 200 \
  --sample-sizes 500 1000 2500 5000 10000 15000 20000 \
  --random-state 20260602
```

Expected bounded shadow-model outputs and row counts:

- `analysis/results/q1_lira_like_appendix/tables/key_metrics.csv`: 4 rows.
- `analysis/results/q1_lira_like_appendix/tables/shadow_fit_summary.csv`: 2 rows.
- `analysis/results/q1_lira_like_appendix/tables/shadow_model_runs.csv`: 16 rows.
- `score_arrays/credit_default_random_forest_shadow_lira_like_neg_loss.npz`: 15,000 members and 15,000 nonmembers.
- `score_arrays/adult_income_random_forest_shadow_lira_like_neg_loss.npz`: 24,421 members and 24,421 nonmembers.
- Each bounded shadow audit-tool directory: 5 `main_metrics` rows, 5 `confidence_intervals` rows, 4 `fixed_threshold_intervals` rows, 6,000 `sample_size_repeats` rows, 30 `sample_size_sensitivity` rows, and 16 `tail_resolution_warnings` rows.

## 9. Q1 Tie-Rule Sensitivity

This check compares strict `score > threshold`, inclusive
`score >= threshold`, and randomized tie-aware low-FPR operating rules for
representative negative-loss rows.

```bash
python3 analysis/run_q1_tie_rule_sensitivity.py \
  --attack-score-subdir expanded_tabular_stage1/attack_scores \
  --output-dir analysis/results/q1_tie_rule_sensitivity \
  --fpr-levels 0.01 0.001
```

Expected tie-rule outputs and row counts:

- `analysis/results/q1_tie_rule_sensitivity/tie_rule_operating_points.csv`: 24 rows.
- `analysis/results/q1_tie_rule_sensitivity/paper_table_tie_rule_sensitivity.csv`: 8 rows.
- `analysis/results/q1_tie_rule_sensitivity/q1_tie_rule_sensitivity_summary.md`: paper-ready table and key readout.

## 10. Q1 Split/Seed Sensitivity

This check redraws the stratified 50/50 member/nonmember split, retrains the
target model using the same integer as the learner seed, recomputes negative
loss scores, and reports five repeated target constructions for three
representative settings.

```bash
python3 analysis/run_q1_split_seed_sensitivity.py \
  --settings credit_default:random_forest:CD/RF \
             credit_default:extra_trees:CD/ET \
             adult_income:random_forest:Adult/RF \
  --seeds 20260602 20260603 20260604 20260605 20260606 \
  --score-names neg_loss \
  --n-estimators 200 \
  --n-jobs -1 \
  --max-iter 1000 \
  --batch-size 50000
```

Expected split/seed outputs and row counts:

- `analysis/results/q1_split_seed_sensitivity/split_seed_metric_rows.csv`: 45 rows.
- `analysis/results/q1_split_seed_sensitivity/split_seed_summary.csv`: 9 rows.
- `analysis/results/q1_split_seed_sensitivity/paper_table_split_seed_sensitivity.csv`: 3 rows.
- `analysis/results/q1_split_seed_sensitivity/q1_split_seed_sensitivity_summary.md`: paper-ready table and design note.

## 11. Q1 Label-Corruption Check

This one-setting check corrupts observed member/nonmember labels for the
`credit_default` / `random_forest` / `neg_loss` score arrays. The corruption
rates are `0`, `0.005`, `0.01`, `0.02`, and `0.05`; the repeat seed is
`20260602 + rate_index * 100000 + repeat`, and the canonical score-array seed is
`20260602 + rate_index * 100000 + 99999`.

Generate repeated metrics, canonical corrupted score arrays, and tail-warning
tables:

```bash
python3 analysis/run_q1_label_uncertainty_stress.py \
  --dataset credit_default \
  --model random_forest \
  --score-name neg_loss \
  --attack-score-subdir expanded_tabular_stage1/attack_scores \
  --output-dir analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss \
  --corruption-rates 0 0.005 0.01 0.02 0.05 \
  --n-repeats 200 \
  --sample-sizes 250 500 1000 2500 5000 10000 15000 \
  --random-state 20260602
```

Run the audit-tool reporting layer for each canonical corrupted array:

```bash
for slug in 0p000 0p005 0p010 0p020 0p050; do
  python3 analysis/run_audit_tool.py \
    --input "analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/score_arrays/neg_loss_label_corruption_${slug}.npz" \
    --input-format npz \
    --output-dir "analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/audit_tool/corruption_${slug}" \
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

Expected label-corruption outputs and row counts:

- `analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/label_uncertainty_repeats.csv`: 5,000 rows.
- `analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/label_uncertainty_summary.csv`: 25 rows.
- `analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/canonical_corruption_metrics.csv`: 25 rows.
- `analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/canonical_score_arrays.csv`: 5 rows.
- `analysis/results/q1_label_uncertainty_stress/credit_default_random_forest_neg_loss/tables/tail_resolution_warnings.csv`: 70 rows.
- Each `score_arrays/neg_loss_label_corruption_<slug>.npz`: 15,000 observed members and 15,000 observed nonmembers.
- Each canonical audit-tool directory under `audit_tool/corruption_<slug>/`: 5 `main_metrics` rows, 5 `confidence_intervals` rows, 4 `fixed_threshold_intervals` rows, 6,000 `sample_size_repeats` rows, 30 `sample_size_sensitivity` rows, and 14 `tail_resolution_warnings` rows.

Canonical label swaps:

| Rate | Slug | Canonical seed | Member-to-nonmember swaps | Nonmember-to-member swaps |
|---:|---|---:|---:|---:|
| 0 | `0p000` | 20360601 | 0 | 0 |
| 0.005 | `0p005` | 20460601 | 75 | 75 |
| 0.01 | `0p010` | 20560601 | 150 | 150 |
| 0.02 | `0p020` | 20660601 | 300 | 300 |
| 0.05 | `0p050` | 20760601 | 750 | 750 |

## 12. Validation Checks Used in the Current Workspace

```bash
python3 -m py_compile analysis/generate_expanded_outputs.py
python3 -m py_compile analysis/generate_final_tables.py
python3 -m py_compile analysis/run_q1_stronger_score_appendix.py
python3 -m py_compile analysis/run_q1_lira_like_appendix.py
python3 -m py_compile analysis/run_q1_tie_rule_sensitivity.py
python3 -m py_compile analysis/run_q1_split_seed_sensitivity.py
python3 -m py_compile analysis/run_q1_label_uncertainty_stress.py
```

The current table QA also checked that Table 3 matches `final_ci_hardening/hardened_confidence_intervals.csv` for 25 dataset/model rows x 3 metrics.
