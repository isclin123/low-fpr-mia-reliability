from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss


def fit_platt_scaler(scores: np.ndarray, labels: np.ndarray) -> LogisticRegression:
    """Fit logistic calibration from one-dimensional attack scores to membership."""
    model = LogisticRegression(solver="lbfgs")
    model.fit(np.asarray(scores).reshape(-1, 1), np.asarray(labels, dtype=int))
    return model


def fit_isotonic_scaler(scores: np.ndarray, labels: np.ndarray) -> IsotonicRegression:
    """Fit monotone nonparametric calibration."""
    model = IsotonicRegression(out_of_bounds="clip")
    model.fit(np.asarray(scores, dtype=float), np.asarray(labels, dtype=int))
    return model


def predict_platt(model: LogisticRegression, scores: np.ndarray) -> np.ndarray:
    return model.predict_proba(np.asarray(scores).reshape(-1, 1))[:, 1]


def predict_isotonic(model: IsotonicRegression, scores: np.ndarray) -> np.ndarray:
    return model.predict(np.asarray(scores, dtype=float))


def expected_calibration_error(
    probabilities: np.ndarray,
    labels: np.ndarray,
    *,
    n_bins: int = 10,
) -> float:
    """Compute equal-width-bin expected calibration error."""
    probabilities = np.asarray(probabilities, dtype=float)
    labels = np.asarray(labels, dtype=int)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0

    for left, right in zip(bins[:-1], bins[1:]):
        if right == 1.0:
            mask = (probabilities >= left) & (probabilities <= right)
        else:
            mask = (probabilities >= left) & (probabilities < right)
        if not np.any(mask):
            continue
        bin_confidence = float(np.mean(probabilities[mask]))
        bin_accuracy = float(np.mean(labels[mask]))
        ece += np.mean(mask) * abs(bin_accuracy - bin_confidence)

    return float(ece)


def calibration_metrics(probabilities: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    probabilities = np.clip(np.asarray(probabilities, dtype=float), 1e-8, 1 - 1e-8)
    labels = np.asarray(labels, dtype=int)
    return {
        "brier": float(brier_score_loss(labels, probabilities)),
        "ece": expected_calibration_error(probabilities, labels),
        "nll": float(log_loss(labels, probabilities)),
    }
