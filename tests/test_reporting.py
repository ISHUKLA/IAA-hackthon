import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.claim_targets import ClaimTargetError
from iaa_hackathon.reporting import (
    average_period_completeness,
    finite_followup_backtest,
    fit_geometric_delay,
    geometric_cdf,
)


def _delay_frame(delays, losses, line="motor", peril="own_damage"):
    loss = pd.to_datetime(losses)
    return pd.DataFrame({
        "claim_id": [f"C{i}" for i in range(len(delays))], "line": line, "peril": peril,
        "loss_date": loss, "report_date": loss + pd.to_timedelta(delays, unit="D"),
    })


def test_geometric_cdf_handles_same_day_and_is_monotone():
    values = geometric_cdf(np.array([-1, 0, 1, 20]), 0.25)
    assert values[0] == 0
    assert values[1] == pytest.approx(0.25)
    assert np.all(np.diff(values) >= 0)
    assert np.all((values >= 0) & (values <= 1))


def test_known_geometric_mechanism_recovers_probability_under_truncation():
    rng = np.random.default_rng(19)
    cutoff = pd.Timestamp("2024-12-31")
    occurrence_age = rng.integers(0, 730, size=12000)
    delay = rng.geometric(0.18, size=12000) - 1
    visible = delay <= occurrence_age
    losses = cutoff - pd.to_timedelta(occurrence_age[visible], unit="D")
    frame = _delay_frame(delay[visible], losses)
    fit = fit_geometric_delay(frame, cutoff=cutoff, line="motor", peril="own_damage")
    assert fit.probability == pytest.approx(0.18, abs=0.015)


def test_complete_same_day_reporting_fit_is_near_one():
    losses = pd.date_range("2024-01-01", periods=100, freq="D")
    fit = fit_geometric_delay(_delay_frame(np.zeros(100, dtype=int), losses), cutoff="2024-12-31", line="motor", peril="glass_hail")
    assert fit.probability > 0.99


def test_sparse_group_fails_explicitly():
    with pytest.raises(ClaimTargetError, match="sparse"):
        fit_geometric_delay(_delay_frame([0, 1], ["2024-01-01", "2024-01-02"]), cutoff="2024-12-31", line="motor", peril="theft")


def test_future_reports_are_excluded_from_cutoff_fit():
    losses = pd.date_range("2022-01-01", periods=40, freq="D")
    base = _delay_frame(np.ones(40, dtype=int), losses)
    future = pd.DataFrame({
        "claim_id": ["F"], "line": ["motor"], "peril": ["own_damage"],
        "loss_date": [pd.Timestamp("2022-06-01")], "report_date": [pd.Timestamp("2024-01-01")],
    })
    fit1 = fit_geometric_delay(base, cutoff="2022-12-31", line="motor", peril="own_damage")
    fit2 = fit_geometric_delay(pd.concat([base, future]), cutoff="2022-12-31", line="motor", peril="own_damage")
    assert fit1.probability == pytest.approx(fit2.probability)


def test_average_period_completeness_and_effective_range():
    result = average_period_completeness(
        pd.Series(pd.to_datetime(["2024-12-31", "2024-01-01"])),
        pd.Series(pd.to_datetime(["2024-12-31", "2024-12-31"])),
        cutoff="2024-12-31", probability=0.2,
    )
    assert result[0] == pytest.approx(0.2)
    assert result[1] > result[0]
    assert np.all((result > 0) & (result <= 1))


def test_finite_followup_is_labelled_not_ultimate():
    losses = pd.date_range("2022-01-01", periods=50, freq="D")
    frame = _delay_frame(np.arange(50) % 5, losses)
    result = finite_followup_backtest(frame, fit_cutoff="2022-12-31", followup_cutoff="2024-12-31")
    assert result[0]["status"] == "available"
    assert "not ultimate" in result[0]["limitation"]
