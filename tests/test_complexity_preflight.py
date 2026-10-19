"""The Step 8 audit must reject incompatible evidence before scoring."""
import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.complexity_preflight import align_predictions, prerequisite_decision


def prediction_fixture():
    return pd.DataFrame({"row_id": ["b", "a"], "prediction": [2.0, 1.0], "fold_id": ["F2023"] * 2, "response_version": ["same"] * 2, "prediction_unit": ["policy_period_cost"] * 2})


def test_aligns_exact_ids_without_using_held_out_outcomes():
    expected = pd.DataFrame({"row_id": ["a", "b"], "observed_net_incurred": [0.0, 4.0]})
    before = align_predictions(expected, prediction_fixture(), fold="F2023", response="same")
    expected["observed_net_incurred"] = [999.0, 0.0]
    after = align_predictions(expected, prediction_fixture(), fold="F2023", response="same")
    np.testing.assert_array_equal(before, [1.0, 2.0])
    np.testing.assert_array_equal(before, after)


@pytest.mark.parametrize("column,value", [("row_id", "a"), ("row_id", "wrong"), ("fold_id", "F2024"), ("response_version", "different"), ("prediction_unit", "annual_rate"), ("prediction", 0.0), ("prediction", np.nan), ("prediction", np.inf)])
def test_rejects_bad_identity_metadata_or_prediction_domain(column, value):
    supplied = prediction_fixture()
    supplied.loc[0, column] = value
    with pytest.raises(ValueError):
        align_predictions(pd.DataFrame({"row_id": ["a", "b"]}), supplied, fold="F2023", response="same")


def test_missing_step7_is_blocked_even_with_passing_prior_checks():
    decision, blockers = prerequisite_decision([], [])
    assert decision == "blocked"
    assert blockers[0].startswith("missing_step7_evidence:")


def test_incompatible_inputs_cannot_be_overridden_by_a_manifest_name():
    decision, blockers = prerequisite_decision(["outputs/step7/manifest.json"], ["upstream hash mismatch"])
    assert decision == "blocked"
    assert "upstream hash mismatch" in blockers
    assert any(item.startswith("step7_evidence_requires_review:") for item in blockers)


def test_verified_step7_and_compatible_inputs_pass_preflight():
    assert prerequisite_decision(["outputs/step7/manifest.json"], [], step7_verified=True) == ("ready", [])


def test_verified_step7_cannot_bypass_an_upstream_mismatch():
    decision, blockers = prerequisite_decision(["outputs/step7/manifest.json"], ["hash mismatch"], step7_verified=True)
    assert decision == "blocked" and blockers == ["hash mismatch"]
