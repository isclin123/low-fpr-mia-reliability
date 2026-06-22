# Audit Tool Interpretation Guide

Date: 2026-06-03

Status: reader-facing guide for interpreting score-array audit outputs.

## Purpose

This guide explains how to read the reusable MIA audit-tool outputs. It is written for paper readers and future users who already have member and non-member attack score arrays, where larger scores mean "more member-like."

The tool does not train a target model and does not create a new attack. It evaluates score arrays and reports point metrics, uncertainty intervals, sample-size sensitivity, and low-FPR tail-resolution warnings.

## Read the Output in This Order

### 1. Check the audit sample sizes

Start with `run_summary.md`, `run_config.json`, and `metrics/main_metrics.csv`.

Record:

- number of member scores;
- number of non-member scores;
- score names;
- target FPR levels;
- bootstrap repeats;
- subsampling repeats and requested sample sizes.

Low-FPR metrics are especially sensitive to the non-member count. A target FPR of 0.1% means that 1,000 non-members provide only one expected false positive, and 5,000 non-members provide only five expected false positives.

### 2. Read tail-resolution warnings before low-FPR TPR

Open `diagnostics/tail_resolution_warnings.csv`.

Use this rule:

| Expected false positives | Warning level | Interpretation |
|---:|---|---|
| `< 1` | severe | The requested FPR is below one expected false positive. Treat the estimate as highly fragile. |
| `1` to `< 5` | warning | The target FPR has limited tail resolution. Interpret with caution. |
| `>= 5` | none | Tail resolution is less fragile, but the estimate is still finite-sample. |

Do not report a low-FPR TPR without also reporting the non-member count or expected false-positive budget.

### 3. Separate AUC from low-FPR TPR

Open `metrics/main_metrics.csv`.

AUC and low-FPR TPR answer different questions:

- AUC measures global separation between member and non-member scores across all thresholds.
- TPR@1%FPR and TPR@0.1%FPR measure performance at specific low false-positive operating points.
- Membership advantage subtracts the target FPR from TPR at that operating point.

A high AUC does not guarantee a high TPR@0.1%FPR. A low TPR@0.1%FPR does not erase the global AUC pattern. Report them separately.

### 4. Use bootstrap intervals for main uncertainty claims

Open `metrics/confidence_intervals.csv`.

Bootstrap intervals are the main uncertainty view because they resample member and non-member score arrays separately. For low-FPR TPR, this includes variation in threshold selection from finite non-member scores.

When writing a claim, include:

- point estimate;
- 95% bootstrap interval;
- number of bootstrap repeats;
- member and non-member counts;
- target FPR.

Safe wording:

> The score had AUC 0.76 with a 95% bootstrap interval of [0.75, 0.77] using 15,000 members and 15,000 non-members.

Avoid:

> The attack reliably achieves 0.76 AUC in general.

The interval describes uncertainty in the available score-array audit, not all possible datasets, target models, or deployments.

### 5. Treat fixed-threshold Wilson intervals as conditional checks

Open `metrics/fixed_threshold_intervals.csv`.

These intervals answer a narrower question. After the non-member scores select a threshold and randomized tie rule for the target FPR, the Wilson interval estimates member-side TPR uncertainty at that fixed threshold.

Use them as a diagnostic:

- useful for checking binomial uncertainty after threshold selection;
- not a replacement for bootstrap intervals;
- not a full low-FPR uncertainty estimate because threshold-selection uncertainty is conditioned away.

Safe wording:

> The fixed-threshold Wilson interval provides a conditional check after threshold selection.

Avoid:

> The Wilson interval is the final uncertainty interval for low-FPR TPR.

### 6. Use repeated subsampling for audit-size sensitivity

Open:

- `subsampling/sample_size_sensitivity.csv`;
- `subsampling/sample_size_repeats.csv`;
- `subsampling/sample_size_skipped.csv`.

Repeated balanced subsampling shows how metrics move when only smaller member and non-member audit samples are available. It is useful for planning and robustness checks.

Report:

- balanced sample size per group;
- number of repeats;
- mean and quantile range;
- instability warning, if present.

Do not treat a small-sample subsampling interval as a substitute for collecting more non-member records at very low FPR.

### 7. Use figures as diagnostics, not standalone proof

The `figures/` directory is useful for quick inspection:

- low-FPR ROC;
- score distributions;
- interval width versus audit size;
- TPR at FPR versus audit size.

Use figures to find patterns and communicate them. Use CSV tables for exact numbers and uncertainty claims.

## Minimal Reporting Template

For any low-FPR MIA audit result, report:

| Item | Required detail |
|---|---|
| Score definition | What score was audited and whether larger means more member-like. |
| Audit sample size | Number of members and non-members. |
| Metric | AUC, TPR@1%FPR, TPR@0.1%FPR, or membership advantage. |
| Threshold handling | Tie-aware randomized thresholding if ties occur. |
| Uncertainty | Bootstrap interval and number of repeats. |
| Conditional check | Fixed-threshold Wilson interval, if reported. |
| Sample-size sensitivity | Repeated balanced subsampling summary, if material. |
| Tail warning | Expected false positives and warning level. |

## Safe Claim Patterns

Use:

> In this audit sample, score X achieved TPR@0.1%FPR of Y with 95% bootstrap interval [L, U], using N non-members. The expected false-positive budget was B.

Use:

> The estimate should be interpreted cautiously because the expected false-positive budget is below five.

Use:

> The audit workflow can evaluate calibrated or stronger attack scores if they are supplied as member/non-member score arrays.

Avoid:

> This proves the model is private.

Avoid:

> This proves the attack works in production.

Avoid:

> This result generalizes to language models or generative models.

Avoid:

> The audit tool is a new MIA attack.

## Relation to the Manuscript

The manuscript uses the audit tool to support a reporting claim: low-FPR MIA metrics should be treated as finite-sample audit estimates. The tool is reusable because it accepts score arrays from any score producer, but the empirical evidence in the current manuscript is limited to simple score-based tabular audits.

Main manuscript claims should cite the selected 1,000-bootstrap hardened intervals. Full-grid appendix intervals from `expanded_tabular_stage1` should be labelled as stage1 50-bootstrap intervals unless separately hardened.

## Reader Checklist

Before trusting a reported low-FPR MIA number, ask:

- How many non-members were used?
- What was the expected false-positive budget?
- Is there a tail-resolution warning?
- Is the number AUC or TPR at a specific FPR?
- Does the interval include threshold-selection variation?
- Are fixed-threshold Wilson intervals being used only as conditional checks?
- Does subsampling show that the estimate changes at smaller audit sizes?
- Is the claim limited to the score arrays and domain actually evaluated?
