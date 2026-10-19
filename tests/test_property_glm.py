import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.property_glm import (
    fit_property_glm, join_address_features, predict_property_cost, zone_calibration,
)


def frames():
    policy = pd.DataFrame({
        "row_id": [f"B{i}" for i in range(12)],
        "line": ["buildings"] * 12,
        "address_id": [f"A{i}" for i in range(12)],
        "period_start": pd.to_datetime(["2022-01-01"] * 12),
        "exposure_clean": [0.5, 1.0] * 6,
        "observed_net_incurred": [0, 120, 0, 200, 0, 300, 0, 150, 0, 180, 0, 220],
        "policyholder_age": list(range(30, 42)),
        "sum_insured_repaired": [100000 + 10000 * i for i in range(12)],
        "days_unoccupied": [0, 4] * 6,
        "voluntary_excess": [100] * 12,
        "compulsory_excess": [200] * 12,
        "construction_type_standardized": ["brick"] * 12,
        "occupancy": ["owner"] * 12,
        "smoke_alarms": [True] * 12,
        "accidental_damage_cover": [False] * 12,
    })
    address = pd.DataFrame({
        "address_id": [f"A{i}" for i in range(12)],
        "flood_zone": [1, 2, 3, 4, 5, None] * 2,
        "elevation_m": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0] * 2,
        "distance_to_river_km": [0.1, None, 0.3, 0.4, 0.5, 0.6] * 2,
        "bedrooms": [1, 2, 3, 4, 2, 3] * 2,
        "property_type": ["flat", "detached", "terraced"] * 4,
        "year_built": [1990, 2000, 2010, 1980, 1995, 2005] * 2,
    })
    return policy, address


def test_address_join_preserves_row_order_and_explicit_missing_flood_zone():
    policy, address = frames()
    result = join_address_features(policy, address.sample(frac=1, random_state=4))
    assert result.row_id.tolist() == policy.row_id.tolist()
    assert result.flood_zone.iloc[0] == "zone_1"
    assert result.flood_zone.iloc[5] == "missing"
    assert len(result) == len(policy)


def test_address_join_rejects_duplicate_missing_and_future_properties():
    policy, address = frames()
    with pytest.raises(ValueError, match="many-to-one"):
        join_address_features(policy, pd.concat([address, address.iloc[[0]]]))
    with pytest.raises(ValueError, match="absent"):
        join_address_features(policy, address.iloc[1:])
    future = address.copy()
    future.loc[0, "year_built"] = 2023
    with pytest.raises(ValueError, match="after"):
        join_address_features(policy, future)


def test_fitted_property_glm_uses_one_exposure_and_reloads():
    policy, address = frames()
    data = join_address_features(policy, address)
    train, valid = data.iloc[:9].copy(), data.iloc[9:].copy()
    prediction, model, meta = fit_property_glm(
        train, valid, line="buildings", base_blocks=["log_sum_insured", "occupancy_security"],
        extra_features=["flood_zone", "elevation_m", "distance_to_river_km", "bedrooms", "property_type", "year_built"],
        alpha=1, max_iter=100,
    )
    assert meta["converged"] and np.isfinite(prediction).all() and (prediction > 0).all()
    np.testing.assert_allclose(prediction, predict_property_cost(
        model, valid, line="buildings", base_blocks=["log_sum_insured", "occupancy_security"],
        extra_features=meta["extra_features"],
    ), rtol=0, atol=0)
    with pytest.raises(ValueError, match="unapproved"):
        fit_property_glm(train, valid, line="buildings", base_blocks=[], extra_features=["observed_net_incurred"], alpha=1, max_iter=100)


def test_zone_calibration_reconciles_totals_and_requires_alignment():
    policy, address = frames()
    data = join_address_features(policy, address)
    actual = data.observed_net_incurred.to_numpy(float)
    prediction = np.full(len(data), 10.0)
    rows = zone_calibration(data, actual, prediction)
    assert sum(x["rows"] for x in rows) == len(data)
    assert sum(x["actual"] for x in rows) == actual.sum()
    assert sum(x["prediction"] for x in rows) == prediction.sum()
    with pytest.raises(ValueError, match="aligned"):
        zone_calibration(data, actual[:-1], prediction)
