"""Behavioral and independent arithmetic tests for the fixed Tweedie metric."""

from __future__ import annotations

import math

import numpy as np
import pytest

from iaa_hackathon.metrics import (
    UndefinedD2Error,
    d2_tweedie_score_15,
    mean_tweedie_deviance_15,
    metric_report,
)


def hand_deviance_15(y: float, mu: float) -> float:
    """Independent p=1.5 arithmetic supplied by the Prompt 04 contract."""
    return 4 * (y / math.sqrt(mu) + math.sqrt(mu) - 2 * math.sqrt(y))


def test_independent_hand_calculation_is_four() -> None:
    y_true = [0.0, 4.0]
    y_pred = [1.0, 1.0]
    hand_mean = sum(hand_deviance_15(y, mu) for y, mu in zip(y_true, y_pred)) / 2
    assert hand_mean == pytest.approx(4.0)
    assert mean_tweedie_deviance_15(y_true, y_pred) == pytest.approx(hand_mean)


def test_empirical_mean_null_scores_zero() -> None:
    y_true = np.array([0.0, 1.0, 4.0, 9.0])
    y_pred = np.repeat(y_true.mean(), len(y_true))
    assert d2_tweedie_score_15(y_true, y_pred) == pytest.approx(0.0, abs=1e-14)


def test_perfect_positive_nonconstant_predictions_score_one() -> None:
    y_true = [0.25, 1.0, 4.0]
    assert d2_tweedie_score_15(y_true, y_true) == pytest.approx(1.0)


def test_deliberately_poor_prediction_is_worse_than_null() -> None:
    y_true = [0.0, 1.0, 4.0, 9.0]
    null = [3.5] * 4
    poor = [0.01, 0.01, 0.01, 0.01]
    assert d2_tweedie_score_15(y_true, poor) < d2_tweedie_score_15(y_true, null)


def test_optional_weights_match_independent_weighted_arithmetic() -> None:
    y_true = [0.0, 4.0, 9.0]
    y_pred = [1.0, 1.0, 4.0]
    weights = [1.0, 2.0, 3.0]
    individual = [hand_deviance_15(y, mu) for y, mu in zip(y_true, y_pred)]
    hand_weighted = sum(w * d for w, d in zip(weights, individual)) / sum(weights)
    assert mean_tweedie_deviance_15(
        y_true, y_pred, sample_weight=weights
    ) == pytest.approx(hand_weighted)


def test_row_loss_and_sqrt_exposure_rate_deviance_totals_are_equivalent() -> None:
    exposure = np.array([0.25, 1.0, 4.0])
    actual_rate = np.array([0.0, 4.0, 9.0])
    predicted_rate = np.array([1.0, 2.0, 6.0])
    actual_row_loss = exposure * actual_rate
    predicted_row_loss = exposure * predicted_rate

    row_mean = mean_tweedie_deviance_15(actual_row_loss, predicted_row_loss)
    rate_weighted_mean = mean_tweedie_deviance_15(
        actual_rate,
        predicted_rate,
        sample_weight=np.sqrt(exposure),
    )
    assert row_mean * len(exposure) == pytest.approx(
        rate_weighted_mean * np.sqrt(exposure).sum()
    )


@pytest.mark.parametrize(
    ("y_true", "y_pred", "weights", "message"),
    [
        ([1.0], [1.0, 2.0], None, "same length"),
        ([1.0, float("nan")], [1.0, 1.0], None, "finite"),
        ([1.0, -1.0], [1.0, 1.0], None, "nonnegative"),
        ([0.0, 1.0], [0.0, 1.0], None, "strictly positive"),
        ([0.0, 1.0], [float("inf"), 1.0], None, "finite"),
        ([0.0, 1.0], [1.0, 1.0], [1.0], "same length"),
        ([0.0, 1.0], [1.0, 1.0], [1.0, -1.0], "nonnegative"),
        ([0.0, 1.0], [1.0, 1.0], [0.0, 0.0], "positive total"),
    ],
)
def test_invalid_inputs_are_rejected(y_true, y_pred, weights, message) -> None:
    with pytest.raises(ValueError, match=message):
        mean_tweedie_deviance_15(y_true, y_pred, sample_weight=weights)


@pytest.mark.parametrize(
    ("y_true", "y_pred", "weights", "message"),
    [
        ([1.0], [1.0], None, "at least two"),
        ([0.0, 0.0], [1.0, 1.0], None, "constant"),
        ([2.0, 2.0, 2.0], [1.0, 2.0, 3.0], None, "constant"),
        ([0.0, 1.0], [1.0, 1.0], [1.0, 0.0], "at least two"),
    ],
)
def test_undefined_d2_is_raised_clearly(y_true, y_pred, weights, message) -> None:
    with pytest.raises(UndefinedD2Error, match=message):
        d2_tweedie_score_15(y_true, y_pred, sample_weight=weights)


def test_mean_deviance_remains_available_when_d2_is_undefined() -> None:
    report = metric_report([0.0, 0.0], [1.0, 1.0])
    assert report["mean_tweedie_deviance"] == pytest.approx(4.0)
    assert report["d2_tweedie_score"] is None
    assert report["d2_status"] == "undefined"
    assert report["competition_pooling_and_weighting_status"] == "unresolved"


def test_metric_report_materializes_one_shot_iterables_once() -> None:
    report = metric_report(
        (value for value in [0.0, 1.0, 4.0]),
        (value for value in [1.0, 1.0, 2.0]),
        sample_weight=(value for value in [1.0, 2.0, 1.0]),
    )
    assert report["d2_status"] == "defined"
    assert report["weighting"] == "explicit_sample_weight"
