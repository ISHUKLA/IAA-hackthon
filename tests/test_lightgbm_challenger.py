import json

import lightgbm as lgb
import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.baselines import BASE_FEATURES
from iaa_hackathon.complexity_preflight import align_predictions
from iaa_hackathon.lightgbm_challenger import FeaturePipeline, assert_identity, fit_model, paired_uncertainty, period_prediction, rate_response, safe_feature_names
from iaa_hackathon.metrics import mean_tweedie_deviance_15


def synthetic(n=512):
    rng = np.random.default_rng(77)
    ages = rng.integers(20, 80, n)
    data = pd.DataFrame({"row_id": [f"r{i}" for i in range(n)], "customer_id": [f"c{i // 2}" for i in range(n)], "line": "motor", "exposure_clean": rng.uniform(.1, 1, n), "observed_net_incurred": rng.poisson(ages / 15), "driver_age": ages.astype(float), "years_licensed": ages - 18, "vehicle_age": rng.integers(0, 15, n), "annual_mileage": rng.uniform(100, 20000, n), "voluntary_excess": 100.0, "compulsory_excess": 200.0, "cover_type": np.where(ages < 40, "young", "other"), "vehicle_use": "private", "body_type": "car", "engine_size_cc": 1000.0, "telematics_opt_in": False, "telematics_score": np.nan})
    data.loc[0, "annual_mileage"] = np.nan
    return data


def parameters():
    return {"objective": "tweedie", "tweedie_variance_power": 1.5, "metric": "None", "num_leaves": 7, "min_data_in_leaf": 10, "learning_rate": .1, "num_threads": 1, "deterministic": True, "force_col_wise": True, "seed": 17, "verbosity": -1}


def fitted(train):
    return fit_model(train, None, line="motor", blocks=[], features=BASE_FEATURES["motor"], params=parameters(), rounds=20)


def test_rate_period_identity_and_exposure_exactly_once():
    train = synthetic()
    y, weight = rate_response(train)
    exposure = train.exposure_clean.to_numpy()
    rate = np.full(len(train), 3.)
    assert mean_tweedie_deviance_15(train.observed_net_incurred, exposure * rate) == pytest.approx(mean_tweedie_deviance_15(y, rate, sample_weight=weight) * weight.mean())
    model, pipeline, _ = fitted(train)
    double = train.copy()
    double["exposure_clean"] *= 2
    np.testing.assert_allclose(period_prediction(model, pipeline, double), 2 * period_prediction(model, pipeline, train))


def test_deterministic_fit_reload_and_held_out_target_independence(tmp_path):
    train = synthetic()
    held_out = synthetic(32)
    model, pipeline, _ = fitted(train)
    repeated, pipeline2, _ = fitted(train)
    assert model.model_to_string() == repeated.model_to_string()
    before = period_prediction(model, pipeline, held_out)
    held_out["observed_net_incurred"] = 1e9
    held_out["status"] = "future_status"
    np.testing.assert_array_equal(before, period_prediction(model, pipeline, held_out))
    np.testing.assert_array_equal(before, period_prediction(repeated, pipeline2, held_out))
    model.save_model(tmp_path / "model.txt")
    state = {"line": pipeline.line, "blocks": pipeline.blocks, "allowed": pipeline.allowed, "vocabularies": pipeline.vocabularies}
    state = json.loads(json.dumps(state))
    restored = FeaturePipeline(**state)
    np.testing.assert_array_equal(before, period_prediction(lgb.Booster(model_file=str(tmp_path / "model.txt")), restored, held_out))
    assert np.isfinite(before).all() and (before > 0).all()


def test_train_only_categories_and_structural_missingness():
    train = synthetic()
    pipeline = FeaturePipeline("motor", [], BASE_FEATURES["motor"]).fit(train)
    held_out = train.iloc[:3].copy()
    held_out["cover_type"] = "never_seen"
    matrix = pipeline.transform(held_out)
    assert matrix.cover_type.isna().all()
    assert "never_seen" not in pipeline.vocabularies["cover_type"]
    assert matrix.annual_mileage.isna().iloc[0]
    assert train.telematics_score.isna().all()
    assert "telematics_score" not in matrix
    assert matrix.index.equals(held_out.index)


@pytest.mark.parametrize("name", ["row_id", "customer_id_clean", "observed_net_incurred", "status", "written_premium", "customer_service_contacts", "telematics_score", "weather_year", "claim_history_after_period_start"])
def test_rejects_identifiers_outcomes_and_unsafe_timing(name):
    with pytest.raises(ValueError):
        safe_feature_names([name], [name])


@pytest.mark.parametrize("field,value", [("exposure_clean", 0.), ("exposure_clean", np.inf), ("observed_net_incurred", -1.), ("observed_net_incurred", np.nan)])
def test_rejects_invalid_exposure_or_response(field, value):
    data = synthetic()
    data.loc[0, field] = value
    with pytest.raises(ValueError):
        rate_response(data)


@pytest.mark.parametrize("field", ["fold", "response", "policy_sha256"])
def test_rejects_incompatible_provenance(field):
    expected = {"fold": "F2023", "response": "repaired", "policy_sha256": "abc"}
    actual = {**expected, field: "changed"}
    with pytest.raises(ValueError):
        assert_identity(actual, expected)


def test_exact_id_alignment_rejects_join_multiplication():
    frame = synthetic(4)
    prediction = pd.DataFrame({"row_id": frame.row_id, "prediction": 1., "fold_id": "F2023", "response_version": "same", "prediction_unit": "policy_period_cost"})
    with pytest.raises(ValueError):
        align_predictions(frame, pd.concat([prediction, prediction.iloc[:1]]), fold="F2023", response="same")


def test_bootstrap_uses_canonical_customer_clusters():
    data = synthetic(40)
    data["customer_id_clean"] = "one_customer"
    y = data.observed_net_incurred.to_numpy(float)
    result = paired_uncertainty(data, np.full(40, 10.), np.full(40, 4.), seed=1, repeats=10)
    assert result["clusters"] == 1
    assert result["mean_deviance_gain_ci95"][0] == pytest.approx(result["mean_deviance_gain"])
