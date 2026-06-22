from __future__ import annotations

from collections.abc import Callable

import numpy as np


MetricFn = Callable[[np.ndarray, np.ndarray], float]


def stratified_bootstrap_ci(
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    metric_fn: MetricFn,
    *,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    random_state: int | None = None,
) -> tuple[float, float, float]:
    """Estimate a metric and percentile CI with stratified bootstrap resampling."""
    rng = np.random.default_rng(random_state)
    member_scores = np.asarray(member_scores, dtype=float)
    nonmember_scores = np.asarray(nonmember_scores, dtype=float)

    point = float(metric_fn(member_scores, nonmember_scores))
    estimates = np.empty(n_bootstrap, dtype=float)

    for i in range(n_bootstrap):
        member_idx = rng.integers(0, len(member_scores), len(member_scores))
        nonmember_idx = rng.integers(0, len(nonmember_scores), len(nonmember_scores))
        estimates[i] = metric_fn(member_scores[member_idx], nonmember_scores[nonmember_idx])

    alpha = 1.0 - confidence
    lower, upper = np.quantile(estimates, [alpha / 2.0, 1.0 - alpha / 2.0])
    return point, float(lower), float(upper)
