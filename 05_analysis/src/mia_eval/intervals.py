from __future__ import annotations

from statistics import NormalDist

import numpy as np

from mia_eval.metrics import operating_point_at_fpr


def wilson_interval(
    successes: float,
    n_trials: int,
    *,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Return a Wilson score interval for a binomial proportion."""
    if n_trials <= 0:
        raise ValueError("n_trials must be positive")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if successes < 0 or successes > n_trials:
        raise ValueError("successes must be in [0, n_trials]")

    alpha = 1.0 - confidence
    z = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    p_hat = successes / n_trials
    z2 = z * z
    denominator = 1.0 + z2 / n_trials
    center = (p_hat + z2 / (2.0 * n_trials)) / denominator
    margin = z * np.sqrt((p_hat * (1.0 - p_hat) / n_trials) + (z2 / (4.0 * n_trials * n_trials)))
    margin /= denominator
    return float(max(0.0, center - margin)), float(min(1.0, center + margin))


def fixed_threshold_tpr_wilson_interval(
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    fpr: float,
    *,
    confidence: float = 0.95,
) -> dict[str, float]:
    """Estimate conditional TPR uncertainty after selecting a low-FPR threshold.

    The threshold and randomized tie fraction follow `operating_point_at_fpr`.
    The Wilson interval is conditional on that selected threshold/tie rule and
    uses the resulting effective member success count.
    """
    member_scores = np.asarray(member_scores, dtype=float)
    nonmember_scores = np.asarray(nonmember_scores, dtype=float)
    if len(member_scores) == 0:
        raise ValueError("member_scores must be non-empty")
    if len(nonmember_scores) == 0:
        raise ValueError("nonmember_scores must be non-empty")

    operating_point = operating_point_at_fpr(member_scores, nonmember_scores, fpr)
    threshold = operating_point["threshold"]
    tie_fraction = operating_point["tie_fraction"]

    member_gt = float(np.sum(member_scores > threshold))
    member_eq = float(np.sum(member_scores == threshold))
    member_successes = member_gt + tie_fraction * member_eq

    nonmember_gt = float(np.sum(nonmember_scores > threshold))
    nonmember_eq = float(np.sum(nonmember_scores == threshold))
    nonmember_false_positives = nonmember_gt + tie_fraction * nonmember_eq

    lower, upper = wilson_interval(member_successes, len(member_scores), confidence=confidence)
    point = member_successes / len(member_scores)
    empirical_fpr = nonmember_false_positives / len(nonmember_scores)

    return {
        "target_fpr": float(fpr),
        "threshold": float(threshold),
        "tie_fraction": float(tie_fraction),
        "empirical_fpr": float(empirical_fpr),
        "point": float(point),
        "ci_lower": lower,
        "ci_upper": upper,
        "ci_width": float(upper - lower),
        "confidence": float(confidence),
        "member_successes_effective": float(member_successes),
        "member_count_gt_threshold": float(member_gt),
        "member_count_eq_threshold": float(member_eq),
        "n_members": float(len(member_scores)),
        "nonmember_false_positives_effective": float(nonmember_false_positives),
        "nonmember_count_gt_threshold": float(nonmember_gt),
        "nonmember_count_eq_threshold": float(nonmember_eq),
        "n_nonmembers": float(len(nonmember_scores)),
    }
