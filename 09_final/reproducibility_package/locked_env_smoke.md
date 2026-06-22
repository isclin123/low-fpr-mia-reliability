# Locked-Environment Smoke Test

Date: 2026-06-03

Status: passed for the audit-tool smoke path with a pinned requirements lock.

## Scope

This test validates the reusable score-array audit-tool examples in a fresh Python virtual environment installed from:

- `05_analysis/requirements-lock.txt`

It validates the fast reporting-layer reproducibility path. It does not rerun the full expanded 5 dataset x 5 model grid or the 1,000-bootstrap hardening run.

## Environment

Temporary environment:

```text
/tmp/mia_repro_lock_smoke_20260603
```

Python:

```text
Python 3.13.5
```

Install commands:

```bash
python3 -m venv /tmp/mia_repro_lock_smoke_20260603
/tmp/mia_repro_lock_smoke_20260603/bin/python -m pip install --upgrade pip
/tmp/mia_repro_lock_smoke_20260603/bin/python -m pip install -r 05_analysis/requirements-lock.txt
```

The installed package freeze was saved to:

- `05_analysis/results/lock_env_smoke_freeze.txt`

## Commands Tested

Example score generation:

```bash
/tmp/mia_repro_lock_smoke_20260603/bin/python 05_analysis/examples/make_audit_tool_examples.py
```

NPZ audit-tool smoke:

```bash
/tmp/mia_repro_lock_smoke_20260603/bin/python 05_analysis/run_audit_tool.py \
  --input 05_analysis/examples/example_scores.npz \
  --input-format npz \
  --output-dir 05_analysis/results/lock_env_smoke_npz \
  --dataset credit_default \
  --model random_forest \
  --n-bootstrap 25 \
  --n-repeats 10 \
  --sample-sizes 250 500 \
  --random-state 20260603
```

CSV audit-tool smoke:

```bash
/tmp/mia_repro_lock_smoke_20260603/bin/python 05_analysis/run_audit_tool.py \
  --input 05_analysis/examples/example_scores.csv \
  --input-format csv \
  --output-dir 05_analysis/results/lock_env_smoke_csv \
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

Both locked-environment smoke runs produced:

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
- four score-distribution figures

Output directories:

- `05_analysis/results/lock_env_smoke_npz/`
- `05_analysis/results/lock_env_smoke_csv/`

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
PASS locked-env audit-tool smoke; NPZ and CSV AUC snapshots match
```

## Remaining Reproducibility Boundary

- The pinned lock validates the fast audit-tool reporting path, not the full expanded empirical rerun.
- Public archival release still needs repository DOI/release URL and licence decisions.
- A container recipe remains optional but could further harden cross-platform reproducibility.
