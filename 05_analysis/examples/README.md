# Audit Tool Examples

This directory contains small score-array examples for `05_analysis/run_audit_tool.py`.

The examples are sampled from the existing core `credit_default` / `random_forest` attack-score artifact. They are intended for CLI/API validation and documentation, not for final paper evidence.

## Regenerate examples

```bash
python3 05_analysis/examples/make_audit_tool_examples.py
```

Outputs:

- `05_analysis/examples/example_scores.npz`
- `05_analysis/examples/example_scores.csv`

## Run the NPZ example

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

## Run the CSV example

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
