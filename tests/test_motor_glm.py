"""Synthetic guards for the unpromoted motor challenger."""

import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.motor_glm import fit_motor_glm, join_motor_features, model_features, predict_motor_cost
from scripts.run_motor_features import score_pair


def sample_policy() -> pd.DataFrame:
    return pd.DataFrame({
        "row_id": ["M1", "M2"], "line": ["motor", "motor"],
        "customer_id_clean": ["00000001", "00000001"], "address_id": ["A1", "A1"],
        "driver_age": [30.0, 40.0], "ncb_years": [2.0, 4.0], "years_licensed": [4.0, 5.0],
        "exposure_clean": [1.0, 0.5], "observed_net_incurred": [0.0, 100.0],
    })


def dimensions() -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = pd.DataFrame({"customer_id": ["00000001"], "marital_status": ["single"],
                              "occupation": ["teacher"], "prior_claims_5y": [0]})
    addresses = pd.DataFrame({"address_id": ["A1"], "region": ["north"]})
    return customers, addresses


def test_join_preserves_motor_rows_and_dimension_values() -> None:
    result = join_motor_features(sample_policy(), *dimensions())
    assert result.row_id.tolist() == ["M1", "M2"]
    assert result.region.tolist() == ["north", "north"]
    assert result.prior_claims_5y.tolist() == [0, 0]


def test_join_rejects_missing_and_duplicate_dimension_rows() -> None:
    customers, addresses = dimensions()
    with pytest.raises(ValueError, match="unmatched"):
        join_motor_features(sample_policy(), customers.iloc[0:0], addresses)
    with pytest.raises(ValueError, match="many-to-one"):
        join_motor_features(sample_policy(), pd.concat([customers, customers]), addresses)


def test_feature_modes_reject_unapproved_and_missing_ncb() -> None:
    frame = sample_policy()
    assert model_features(frame, mode="univariate", extras=["driver_age"], blocks=[])[1] == ["driver_age"]
    with pytest.raises(ValueError, match="include NCB"):
        model_features(frame, mode="s6", extras=["region"], blocks=[])
    with pytest.raises(ValueError, match="unapproved"):
        model_features(frame, mode="s6", extras=["ncb_years", "observed_net_incurred"], blocks=[])


def test_univariate_fit_reload_and_exposure_applied_once() -> None:
    train = pd.concat([sample_policy()] * 3, ignore_index=True)
    train.row_id = [f"T{i}" for i in range(len(train))]
    valid = sample_policy().iloc[[0]].copy()
    prediction, model, metadata = fit_motor_glm(train, valid, mode="univariate", extras=["ncb_years"], blocks=[], alpha=1.0, max_iter=100)
    assert metadata["features"] == ["ncb_years"]
    assert np.array_equal(prediction, predict_motor_cost(model, valid, mode="univariate", extras=["ncb_years"], blocks=[]))
    doubled = valid.copy()
    doubled["exposure_clean"] *= 2
    assert predict_motor_cost(model, doubled, mode="univariate", extras=["ncb_years"], blocks=[])[0] == pytest.approx(2 * prediction[0])


def test_large_claim_row_sensitivity_only_changes_scoring_population() -> None:
    actual = np.array([0.0, 11_894_276.93, 12.0])
    prediction = np.array([1.0, 50.0, 11.0])
    scored = score_pair(actual, prediction, np.array([True, False, True]))
    assert scored["all_rows"]["rows"] == 3
    assert scored["without_large_claim_row"]["rows"] == 2
    assert actual[1] == 11_894_276.93
    assert prediction[1] == 50.0
