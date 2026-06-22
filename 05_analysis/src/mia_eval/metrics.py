from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score


def threshold_at_fpr(nonmember_scores: np.ndarray, fpr: float) -> float:
    """Return a score threshold whose empirical false positive rate is near fpr."""
    if not 0 < fpr < 1:
        raise ValueError("fpr must be between 0 and 1")
    nonmember_scores = np.asarray(nonmember_scores, dtype=float)
    return float(np.quantile(nonmember_scores, 1.0 - fpr, method="higher"))


def operating_point_at_fpr(
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    fpr: float,
) -> dict[str, float]:
    """Return a tie-aware operating point at a target FPR.

    If many non-members have exactly the threshold score, counting all ties with
    `>= threshold` can exceed the requested low-FPR operating point. This uses
    randomized tie-breaking at the threshold and reports the expected TPR/FPR.
    """
    threshold = threshold_at_fpr(nonmember_scores, fpr)
    member_scores = np.asarray(member_scores, dtype=float)
    nonmember_scores = np.asarray(nonmember_scores, dtype=float)

    non_gt = float(np.mean(nonmember_scores > threshold))
    non_eq = float(np.mean(nonmember_scores == threshold))
    if non_eq > 0:
        tie_fraction = float(np.clip((fpr - non_gt) / non_eq, 0.0, 1.0))
    else:
        tie_fraction = 0.0

    member_gt = float(np.mean(member_scores > threshold))
    member_eq = float(np.mean(member_scores == threshold))
    actual_fpr = non_gt + tie_fraction * non_eq
    tpr = member_gt + tie_fraction * member_eq
    return {
        "threshold": float(threshold),
        "tie_fraction": tie_fraction,
        "fpr": float(actual_fpr),
        "tpr": float(tpr),
        "membership_advantage": float(tpr - actual_fpr),
    }


def tpr_at_fpr(member_scores: np.ndarray, nonmember_scores: np.ndarray, fpr: float) -> float:
    """Compute tie-aware expected TPR at a target FPR."""
    return operating_point_at_fpr(member_scores, nonmember_scores, fpr)["tpr"]


def membership_advantage_at_fpr(member_scores: np.ndarray, nonmember_scores: np.ndarray, fpr: float) -> float:
    """Compute tie-aware TPR - FPR at a target FPR."""
    return operating_point_at_fpr(member_scores, nonmember_scores, fpr)["membership_advantage"]


def attack_auc(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> float:
    """Compute AUC for member vs non-member scores."""
    y_true = np.concatenate([
        np.ones(len(member_scores), dtype=int),
        np.zeros(len(nonmember_scores), dtype=int),
    ])
    scores = np.concatenate([member_scores, nonmember_scores])
    return float(roc_auc_score(y_true, scores))


def membership_advantage(member_scores: np.ndarray, nonmember_scores: np.ndarray, threshold: float) -> float:
    """Compute TPR - FPR at a fixed threshold."""
    tpr = np.mean(np.asarray(member_scores) >= threshold)
    fpr = np.mean(np.asarray(nonmember_scores) >= threshold)
    return float(tpr - fpr)
