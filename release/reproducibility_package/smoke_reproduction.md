# Smoke Reproduction Path

Date: 2026-06-03

Purpose: provide a fast check that the reusable score-array audit tool works without rerunning the full expanded experiment.

## Preconditions

- Run from project root.
- Install dependencies from `analysis/requirements.txt`.
- Existing core score arrays should be present under `analysis/results/core/attack_scores/`.

## Commands

```bash
python3 analysis/examples/make_audit_tool_examples.py
```

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

## Expected Smoke Outputs

Each audit-tool example should write:

- `run_config.json`
- `run_summary.md`
- `metrics/main_metrics.csv`
- `metrics/confidence_intervals.csv`
- `metrics/fixed_threshold_intervals.csv`
- `subsampling/sample_size_repeats.csv`
- `subsampling/sample_size_sensitivity.csv`
- `subsampling/sample_size_skipped.csv`
- `diagnostics/tail_resolution_warnings.csv`
- `figures/`

## Current Validated Snapshot

The current NPZ and CSV examples produced matching AUC snapshots for the same sampled score data. The NPZ summary reports:

| Attack score | AUC |
|---|---:|
| neg_loss | 0.7699 |
| modified_entropy | 0.7699 |
| confidence | 0.7425 |
| neg_entropy | 0.7425 |

The example deliberately uses only 25 bootstrap repeats and 10 subsampling repeats so it is a fast validation path, not final-paper evidence.

