"""Fixed-power Tweedie metric utilities for the Step 1 contract."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
from sklearn.metrics import d2_tweedie_score, mean_tweedie_deviance


TWEEDIE_POWER = 1.5
PROVISIONAL_POOLING = "pooled_policy_period_rows"
PROVISIONAL_WEIGHTING = "unweighted_unless_explicit_sample_weight_is_supplied"


class UndefinedD2Error(ValueError):
    """Raised when the null deviance required by D² is undefined or zero."""


def _as_vector(values: Iterable[float], name: str) -> np.ndarray:
    try:
        materialized = values if isinstance(values, np.ndarray) else list(values)
        vector = np.asarray(materialized, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if vector.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if vector.size == 0:
        raise ValueError(f"{name} must contain at least one value")
    if not np.isfinite(vector).all():
        raise ValueError(f"{name} must contain only finite values")
    return vector


def _validated_inputs(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    sample_weight: Iterable[float] | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    actual = _as_vector(y_true, "y_true")
    predicted = _as_vector(y_pred, "y_pred")
    if actual.size != predicted.size:
        raise ValueError("y_true and y_pred must have the same length")
    if np.any(actual < 0):
        raise ValueError("y_true must be nonnegative for Tweedie power 1.5")
    if np.any(predicted <= 0):
        raise ValueError("y_pred must be strictly positive for Tweedie power 1.5")

    weights = None
    if sample_weight is not None:
        weights = _as_vector(sample_weight, "sample_weight")
        if weights.size != actual.size:
            raise ValueError("sample_weight must have the same length as y_true")
        if np.any(weights < 0):
            raise ValueError("sample_weight must be nonnegative")
        if float(weights.sum()) <= 0:
            raise ValueError("sample_weight must have positive total weight")
    return actual, predicted, weights


def mean_tweedie_deviance_15(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    *,
    sample_weight: Iterable[float] | None = None,
) -> float:
    """Return standard mean Tweedie deviance at the fixed power 1.5."""
    actual, predicted, weights = _validated_inputs(y_true, y_pred, sample_weight)
    return float(
        mean_tweedie_deviance(
            actual,
            predicted,
            sample_weight=weights,
            power=TWEEDIE_POWER,
        )
    )


def d2_tweedie_score_15(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    *,
    sample_weight: Iterable[float] | None = None,
) -> float:
    """Return standard D² Tweedie at power 1.5, rejecting undefined cases."""
    actual, predicted, weights = _validated_inputs(y_true, y_pred, sample_weight)
    effective = actual if weights is None else actual[weights > 0]
    if effective.size < 2:
        raise UndefinedD2Error("D² requires at least two positive-weight observations")
    if np.all(effective == effective[0]):
        raise UndefinedD2Error("D² is undefined when the positive-weight target is constant")
    score = float(
        d2_tweedie_score(
            actual,
            predicted,
            sample_weight=weights,
            power=TWEEDIE_POWER,
        )
    )
    if not np.isfinite(score):
        raise UndefinedD2Error("D² is undefined for these inputs")
    return score


def metric_report(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    *,
    sample_weight: Iterable[float] | None = None,
) -> dict[str, Any]:
    """Return a labelled local report without masking an undefined D²."""
    actual, predicted, weights = _validated_inputs(y_true, y_pred, sample_weight)
    deviance = mean_tweedie_deviance_15(
        actual, predicted, sample_weight=weights
    )
    try:
        d2 = d2_tweedie_score_15(actual, predicted, sample_weight=weights)
        d2_status = "defined"
        d2_error = None
    except UndefinedD2Error as exc:
        d2 = None
        d2_status = "undefined"
        d2_error = str(exc)
    return {
        "metric": "Tweedie D² score",
        "power": TWEEDIE_POWER,
        "mean_tweedie_deviance": deviance,
        "d2_tweedie_score": d2,
        "d2_status": d2_status,
        "d2_error": d2_error,
        "pooling": PROVISIONAL_POOLING,
        "weighting": (
            PROVISIONAL_WEIGHTING if weights is None else "explicit_sample_weight"
        ),
        "competition_pooling_and_weighting_status": "unresolved",
    }
