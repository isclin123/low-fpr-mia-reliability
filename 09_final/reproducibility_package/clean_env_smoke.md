# Clean-Environment Smoke Test

Date: 2026-06-03

Status: passed for the audit-tool smoke path.

Scope:

- This test validates that the reusable score-array audit-tool examples run in a newly created temporary Python virtual environment.
- It does not rerun the full expanded 5 dataset x 5 model experiment.
- It was followed by a pinned-lock smoke validation recorded in `locked_env_smoke.md`.

## Environment

Temporary environment:

```text
/tmp/mia_repro_smoke_20260603
```

Python:

```text
Python 3.13.5
```

Installed command:

```bash
python3 -m venv /tmp/mia_repro_smoke_20260603
/tmp/mia_repro_smoke_20260603/bin/python -m pip install --upgrade pip
/tmp/mia_repro_smoke_20260603/bin/python -m pip install -r 05_analysis/requirements.txt
```

Observed package versions in the clean environment:

| Package | Version |
|---|---:|
| numpy | 2.4.6 |
| pandas | 3.0.3 |
| scikit-learn | 1.9.0 |
| scipy | 1.17.1 |
| matplotlib | 3.10.9 |
| seaborn | 0.13.2 |
| joblib | 1.5.3 |
| xlrd | 2.0.2 |

## Commands Tested

Example score generation:

```bash
/tmp/mia_repro_smoke_20260603/bin/python 05_analysis/examples/make_audit_tool_examples.py
```

NPZ audit-tool smoke:

```bash
/tmp/mia_repro_smoke_20260603/bin/python 05_analysis/run_audit_tool.py \
  --input 05_analysis/examples/example_scores.npz \
  --input-format npz \
  --output-dir 05_analysis/results/clean_env_smoke_npz \
  --dataset credit_default \
  --model random_forest \
  --n-bootstrap 25 \
  --n-repeats 10 \
  --sample-sizes 250 500 \
  --random-state 20260603
```

CSV audit-tool smoke:

```bash
/tmp/mia_repro_smoke_20260603/bin/python 05_analysis/run_audit_tool.py \
  --input 05_analysis/examples/example_scores.csv \
  --input-format csv \
  --output-dir 05_analysis/results/clean_env_smoke_csv \
  --score-names neg_loss confidence neg_entropy modified_entropy \
  --membership-column membership \
  --dataset credit_default \
  --model random_forest \
  --n-bootstrap 25 \
  --n-repeats 10 \
  --sample-sizes 250 500 \
  --random-state 20260603
```

## Outputs Checked

Both clean-environment smoke runs produced:

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
- `figures/interval_width_vs_audit_size.png`
- `figures/tpr_at_fpr_vs_audit_size.png`

Output directories:

- `05_analysis/results/clean_env_smoke_npz/`
- `05_analysis/results/clean_env_smoke_csv/`

## Validation Snapshot

The NPZ and CSV smoke paths produced matching AUC snapshots:

| Attack score | AUC |
|---|---:|
| confidence | 0.730227 |
| modified_entropy | 0.757341 |
| neg_entropy | 0.730227 |
| neg_loss | 0.757341 |

Validation command result:

```text
PASS clean-env audit-tool smoke; NPZ and CSV AUC snapshots match
```

## Remaining Reproducibility Boundary

- The current `requirements.txt` is unpinned, so the clean environment installed newer packages than the original observed workspace environment.
- A pinned lockfile was later created and this smoke path was rerun; see `09_final/reproducibility_package/locked_env_smoke.md`.
- Full expanded experiment reproduction remains a heavier path and was not rerun in this clean environment.
