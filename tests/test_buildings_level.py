import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.buildings_level import (
    aggregate_ae,
    apply_buildings_uplift,
    calculate_uplift,
    exposure_weighted_average_ae,
)


def test_aggregate_ae_is_actual_over_aggregate_prediction():
    assert aggregate_ae(np.array([20.0, 30.0]), np.array([10.0, 20.0])) == pytest.approx(50 / 30)


def test_average_ae_weights_fold_ratios_by_total_exposure():
    result = exposure_weighted_average_ae(
        {"F2023": 1.2, "F2024": 0.9}, {"F2023": 100.0, "F2024": 300.0}
    )
    assert result == pytest.approx((1.2 * 100 + 0.9 * 300) / 400)


def test_half_gap_factor_and_1_05_upper_cap():
    uncapped = calculate_uplift(1.0842400497233966)
    assert uncapped["factor"] == pytest.approx(1.0421200248616982)
    assert uncapped["cap_binding"] is False
    capped = calculate_uplift(1.20)
    assert capped["uncapped_factor"] == pytest.approx(1.10)
    assert capped["factor"] == pytest.approx(1.05)
    assert capped["cap_binding"] is True


def test_uplift_changes_buildings_only_and_preserves_order():
    parent = pd.DataFrame({
        "row_id": ["M1", "B1", "C1", "B2"],
        "prediction": [10.0, 20.0, 30.0, 40.0],
    })
    result = apply_buildings_uplift(parent, 1.04)
    assert result.row_id.tolist() == parent.row_id.tolist()
    np.testing.assert_array_equal(result.prediction.to_numpy(), [10.0, 20.8, 30.0, 41.6])
    np.testing.assert_array_equal(
        result.loc[result.row_id.str.startswith(("M", "C")), "prediction"].to_numpy(),
        parent.loc[parent.row_id.str.startswith(("M", "C")), "prediction"].to_numpy(),
    )


@pytest.mark.parametrize("bad", [np.nan, np.inf, -0.1])
def test_invalid_factor_rejected(bad):
    frame = pd.DataFrame({"row_id": ["B1"], "prediction": [1.0]})
    with pytest.raises(ValueError):
        apply_buildings_uplift(frame, bad)


def test_invalid_or_misaligned_ae_data_rejected():
    with pytest.raises(ValueError):
        aggregate_ae(np.array([1.0]), np.array([0.0]))
    with pytest.raises(ValueError):
        exposure_weighted_average_ae({"F2023": 1.0}, {"F2024": 10.0})
