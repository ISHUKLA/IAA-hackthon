import pandas as pd
import pytest

from iaa_hackathon.claim_targets import (
    ClaimTargetError,
    add_observed_components,
    apply_reported_claim_scenario,
    build_claim_crosswalk,
    build_observed_response,
    policy_catalog,
    validate_claims,
    validate_policy_periods,
)


def _claims(rows):
    defaults = {
        "claim_id": "C1", "policy_id": "P1", "line": "motor", "peril": "own_damage",
        "loss_date": "2023-06-01", "report_date": "2023-06-02", "status": "closed",
        "paid_to_date": 100.0, "incurred_to_date": 100.0, "recoveries": 10.0,
    }
    return pd.DataFrame([{**defaults, **row} for row in rows])


def _policy(rows=None):
    rows = rows or [{"row_id": "R1", "policy_id": "P1", "period_start": "2023-01-01", "period_end": "2023-12-31"}]
    frame = pd.DataFrame(rows)
    frame["line"] = "motor"
    frame["split"] = "train"
    frame["exposure_raw"] = 1.0
    frame["exposure_clean"] = 1.0
    return {"motor": frame}


def _link(claims, policies=None, strict=True):
    return build_claim_crosswalk(
        claims, policies or _policy(), cutoff="2024-12-31", source_claims_sha256="a" * 64, strict=strict
    )


def test_inclusive_boundaries_and_next_year_report_use_loss_date():
    claims = _claims([
        {"claim_id": "C1", "loss_date": "2023-01-01"},
        {"claim_id": "C2", "loss_date": "2023-12-31", "report_date": "2024-01-15"},
    ])
    result = _link(claims)
    assert result["matched_row_id"].tolist() == ["R1", "R1"]


def test_midterm_rows_are_selected_by_loss_date():
    policies = _policy([
        {"row_id": "R1", "policy_id": "P1", "period_start": "2023-01-01", "period_end": "2023-06-30"},
        {"row_id": "R2", "policy_id": "P1", "period_start": "2023-07-01", "period_end": "2023-12-31"},
    ])
    claims = _claims([
        {"claim_id": "C1", "loss_date": "2023-06-30", "report_date": "2023-07-02"},
        {"claim_id": "C2", "loss_date": "2023-07-01", "report_date": "2023-07-02"},
    ])
    assert _link(claims, policies)["matched_row_id"].tolist() == ["R1", "R2"]


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"line": "contents"}, "unknown_line"),
        ({"policy_id": "NOPE"}, "unknown_policy"),
        ({"loss_date": "2022-12-31", "report_date": "2023-01-01"}, "before_first_supplied_coverage"),
        ({"loss_date": "2024-01-01", "report_date": "2024-01-02"}, "after_last_supplied_coverage"),
    ],
)
def test_unmatched_reasons(change, reason):
    result = _link(_claims([{**change}]), strict=False)
    assert result.loc[0, "disposition"] == "unmatched"
    assert result.loc[0, "exception_reason"] == reason


def test_wrong_known_line_is_not_allowed_to_cross_match():
    motor = _policy()["motor"]
    contents = motor.iloc[0:0].copy()
    policies = {"motor": motor, "contents": contents}
    claim = _claims([{"line": "contents"}])
    result = _link(claim, policies, strict=False)
    assert result.loc[0, "exception_reason"] == "unknown_policy"
    assert pd.isna(result.loc[0, "matched_row_id"])


def test_gap_is_not_attached_to_nearest_period():
    policies = _policy([
        {"row_id": "R1", "policy_id": "P1", "period_start": "2023-01-01", "period_end": "2023-03-31"},
        {"row_id": "R2", "policy_id": "P1", "period_start": "2023-07-01", "period_end": "2023-12-31"},
    ])
    result = _link(_claims([{"loss_date": "2023-05-01"}]), policies)
    assert result.loc[0, "exception_reason"] == "between_supplied_periods"
    assert pd.isna(result.loc[0, "matched_row_id"])


def test_overlaps_fail_validation_and_are_ambiguous_if_inspected():
    policies = _policy([
        {"row_id": "R1", "policy_id": "P1", "period_start": "2023-01-01", "period_end": "2023-08-31"},
        {"row_id": "R2", "policy_id": "P1", "period_start": "2023-07-01", "period_end": "2023-12-31"},
    ])
    with pytest.raises(ClaimTargetError, match="overlapping"):
        validate_policy_periods(policy_catalog(policies))
    result = _link(_claims([{"loss_date": "2023-07-10"}]), policies, strict=False)
    assert result.loc[0, "match_count"] == 2
    assert result.loc[0, "disposition"] == "ambiguous_multiple_match"


def test_repeated_claim_id_fails():
    with pytest.raises(ClaimTargetError, match="claim_id"):
        validate_claims(_claims([{}, {}]), "2024-12-31")


def test_observed_response_preserves_zero_rows_and_claim_counts():
    policies = _policy([
        {"row_id": "R1", "policy_id": "P1", "period_start": "2023-01-01", "period_end": "2023-12-31"},
        {"row_id": "R2", "policy_id": "P2", "period_start": "2023-01-01", "period_end": "2023-12-31"},
    ])
    claims = _claims([
        {"claim_id": "C1", "peril": "own_damage", "incurred_to_date": 100.0, "paid_to_date": 100.0, "recoveries": 10.0},
        {"claim_id": "C2", "peril": "theft", "incurred_to_date": 0.0, "paid_to_date": 0.0, "recoveries": 0.0},
        {"claim_id": "C3", "status": "repudiated", "incurred_to_date": 0.0, "paid_to_date": 0.0, "recoveries": 0.0},
    ])
    response, peril = build_observed_response(_link(claims, policies), policies)
    first = response.set_index("row_id").loc["R1"]
    second = response.set_index("row_id").loc["R2"]
    assert first["observed_net_incurred"] == 90.0
    assert first["accepted_reported_claim_count"] == 2
    assert first["positive_observed_cost_claim_count"] == 1
    assert second["observed_net_incurred"] == 0.0
    assert len(peril) == 2


def test_unknown_status_and_negative_net_fail_without_clipping():
    linked = _link(_claims([{"status": "mystery"}]))
    with pytest.raises(ClaimTargetError, match="unknown"):
        add_observed_components(linked)
    linked = _link(_claims([{"incurred_to_date": 5.0, "paid_to_date": 0.0, "recoveries": 10.0}]), strict=False)
    with pytest.raises(ClaimTargetError, match="negative observed"):
        add_observed_components(linked)


def test_scenario_identity_release_strengthening_and_recovery_once():
    claims = _claims([{"paid_to_date": 80.0, "incurred_to_date": 100.0, "recoveries": 10.0}])
    assert apply_reported_claim_scenario(claims, case_multiplier=1.0).iloc[0] == 90.0
    assert apply_reported_claim_scenario(claims, case_multiplier=0.8).iloc[0] == 86.0
    assert apply_reported_claim_scenario(claims, case_multiplier=1.2).iloc[0] == 94.0
    assert apply_reported_claim_scenario(claims, case_multiplier=1.0, future_recovery=5.0).iloc[0] == 85.0


def test_closed_claim_unchanged_and_invalid_scenario_rejected():
    claims = _claims([{"paid_to_date": 100.0, "incurred_to_date": 100.0, "recoveries": 0.0}])
    assert apply_reported_claim_scenario(claims, case_multiplier=0.2).iloc[0] == 100.0
    with pytest.raises(ClaimTargetError):
        apply_reported_claim_scenario(claims, case_multiplier=-1.0)
