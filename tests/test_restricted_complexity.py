import joblib
import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.baselines import add_feature_blocks
from iaa_hackathon.restricted_complexity import FEATURE, ContentsRefinement, insured_tent, promotion_decision


BLOCKS = ["log_sum_insured", "household_use", "security_value"]


def fixture():
    rng = np.random.default_rng(33)
    n = 512
    data = pd.DataFrame({"row_id": [f"r{x}" for x in range(n)], "policyholder_age": rng.integers(20, 80, n), "sum_insured_repaired": np.exp(rng.normal(10.5, .5, n)), "voluntary_excess": 100., "compulsory_excess": 200., "tenure": np.where(rng.uniform(size=n) < .5, "owner", "renter"), "security_level": "locks", "accidental_damage_cover": True, "works_from_home": False, "lodgers": False, "bicycle_cover": True, "high_value_items": False, "exposure_clean": rng.uniform(.2, 1, n), "observed_net_incurred": rng.poisson(4, n)})
    data.loc[0, "sum_insured_repaired"] = np.nan
    return data


def model_for(train):
    _, names = add_feature_blocks(train, "contents", BLOCKS)
    return ContentsRefinement(BLOCKS, names).fit(train)


def test_tent_geometry_units_and_neutral_missingness():
    knots = np.log1p([100., 200., 300.]).tolist()
    actual = insured_tent(pd.Series([0., 100., 200., 300., 1000., np.nan]), knots)
    np.testing.assert_allclose(actual, [0., 0., 1., 0., 0., 0.])
    with pytest.raises(ValueError):
        insured_tent(pd.Series([-1.]), knots)
    with pytest.raises(ValueError):
        insured_tent(pd.Series([200.]), [1., 1., 3.])


def test_training_knots_and_single_added_feature_preserve_original_values():
    train = fixture()
    preserved = train.copy(deep=True)
    model = model_for(train)
    expected = np.quantile(np.log1p(train.sum_insured_repaired.dropna()), [.2, .5, .8])
    np.testing.assert_array_equal(model.knots, expected)
    matrix = model.matrix(train)
    assert matrix.columns.tolist() == [*model.source_features, FEATURE]
    assert matrix[FEATURE].iloc[0] == 0
    assert matrix.sum_insured_repaired.isna().iloc[0]
    assert matrix.index.equals(train.index)
    pd.testing.assert_frame_equal(train, preserved)


def test_determinism_reload_outcome_independence_and_exposure(tmp_path):
    train = fixture()
    model = model_for(train)
    repeated = model_for(train)
    valid = train.iloc[:40].copy()
    valid["tenure"] = "unseen"
    before = model.predict(valid)
    np.testing.assert_array_equal(before, repeated.predict(valid))
    valid["observed_net_incurred"] = 1e10
    valid["status"] = "future_status"
    valid["row_id"] = [f"different{x}" for x in range(len(valid))]
    np.testing.assert_array_equal(before, model.predict(valid))
    valid["exposure_clean"] *= 2
    np.testing.assert_allclose(2 * before, model.predict(valid))
    joblib.dump(model, tmp_path / "refinement.joblib")
    np.testing.assert_array_equal(model.predict(valid), joblib.load(tmp_path / "refinement.joblib").predict(valid))
    assert np.isfinite(before).all() and (before > 0).all()


def test_response_or_id_cannot_be_added_as_a_predictor():
    train = fixture()
    _, names = add_feature_blocks(train, "contents", BLOCKS)
    for invalid in ("row_id", "observed_net_incurred", "claim_history"):
        with pytest.raises(ValueError):
            ContentsRefinement(BLOCKS, [*names, invalid]).fit(train)


def test_every_gate_required_and_no_failed_gate_can_promote():
    passed = {str(number): {"status": "pass"} for number in range(1, 8)}
    assert promotion_decision(passed) == "promote_candidate"
    for number in passed:
        changed = {**passed, number: {"status": "fail"}}
        assert promotion_decision(changed) == "retain_benchmark"
    with pytest.raises(ValueError):
        promotion_decision({"1": {"status": "pass"}})
    assert promotion_decision({**passed, "5": {"status": "blocked"}}) == "blocked"
