import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.conditional_ultimate import bridge_response
from iaa_hackathon.reporting import average_period_completeness


def fixture():
    policies = pd.DataFrame({
        "row_id": ["a", "b"], "line": ["motor", "motor"],
        "period_start": ["2021-01-01", "2022-01-01"],
        "period_end": ["2021-12-31", "2022-12-31"],
        "exposure_clean": [1.0, 1.0], "observed_net_incurred": [100.0, 0.0],
    })
    claims = pd.DataFrame({
        "matched_row_id": ["a"], "line": ["motor"], "peril": ["own_damage"],
        "report_date": ["2021-02-01"], "accepted_for_observed": [True],
        "observed_net_incurred": [100.0],
    })
    return policies, claims


def test_ibnr_bridge_is_additive_and_uses_reporting_fraction():
    policies, claims = fixture()
    p = 0.01
    result, details = bridge_response(
        policies, claims, {("motor", "own_damage"): p},
        mature_rate_years=(2021, 2022), rate_cutoff="2022-12-31", valuation_date="2024-12-31",
    )
    c_rate = average_period_completeness(policies.period_start, policies.period_end, cutoff="2022-12-31", probability=p)
    rate = 100.0 / c_rate.sum()
    c_val = average_period_completeness(policies.period_start, policies.period_end, cutoff="2024-12-31", probability=p)
    np.testing.assert_allclose(result.estimated_unreported_net_cost, rate * (1-c_val))
    np.testing.assert_allclose(result.conditional_ultimate_net_cost, result.observed_net_incurred + result.estimated_unreported_net_cost)
    assert details[0]["mature_reported_cost"] == 100.0
    assert result.loc[1, "conditional_ultimate_net_cost"] > 0


def test_bridge_rejects_wrong_claim_universe():
    policies, claims = fixture()
    claims.loc[0, "observed_net_incurred"] = 101.0
    with pytest.raises(ValueError, match="reconcile"):
        bridge_response(policies, claims, {("motor", "own_damage"): 0.01}, mature_rate_years=(2021, 2022), rate_cutoff="2022-12-31", valuation_date="2024-12-31")


def test_bridge_rejects_unavailable_mature_years_and_fit_groups():
    policies, claims = fixture()
    with pytest.raises(ValueError, match="mature"):
        bridge_response(policies, claims, {("motor", "own_damage"): 0.01}, mature_rate_years=(2020,), rate_cutoff="2022-12-31", valuation_date="2024-12-31")
    with pytest.raises(ValueError, match="groups"):
        bridge_response(policies, claims, {("motor", "glass_hail"): 0.01}, mature_rate_years=(2021, 2022), rate_cutoff="2022-12-31", valuation_date="2024-12-31")


def test_rate_uses_only_claims_reported_by_declared_cutoff():
    policies, claims = fixture()
    claims = pd.concat([claims, pd.DataFrame({
        "matched_row_id": ["b"], "line": ["motor"], "peril": ["own_damage"],
        "report_date": ["2023-03-01"], "accepted_for_observed": [True],
        "observed_net_incurred": [100.0],
    })], ignore_index=True)
    policies.loc[1, "observed_net_incurred"] = 100.0
    result, detail = bridge_response(
        policies, claims, {("motor", "own_damage"): 0.01},
        mature_rate_years=(2021, 2022), rate_cutoff="2022-12-31", valuation_date="2024-12-31",
    )
    assert detail[0]["mature_reported_cost"] == 100.0
    assert result.observed_net_incurred.sum() == 200.0


def test_bridge_rejects_a_rate_cutoff_after_valuation():
    policies, claims = fixture()
    with pytest.raises(ValueError, match="cutoff"):
        bridge_response(policies, claims, {("motor", "own_damage"): 0.01}, mature_rate_years=(2021, 2022), rate_cutoff="2025-01-01", valuation_date="2024-12-31")
