"""Raw-data-free behavioral checks for Step 2 cleaning primitives."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from iaa_hackathon.cleaning import (
    DataQualityError,
    derive_exposure,
    derive_sum_insured_candidate,
    guarded_left_join,
    motor_quality_flags,
    normalize_customer_id,
    normalize_customer_ids,
    validate_unique_dimension,
)


CUSTOMERS = {"00000123", "12345678"}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("123", ("00000123", True, "leading_zero_recovered")),
        ("12345678", ("12345678", False, "already_canonical")),
        (None, (None, False, "missing")),
        ("12A", (None, False, "malformed")),
        ("123456789", (None, False, "overlong")),
        ("999", (None, False, "unresolved_reference")),
    ],
)
def test_customer_id_normalization(value, expected) -> None:
    assert normalize_customer_id(value, CUSTOMERS) == expected


def test_customer_series_is_idempotent_and_never_materializes_null_text() -> None:
    first = normalize_customer_ids(pd.Series(["123", "12345678", None]), CUSTOMERS)
    second = normalize_customer_ids(first["customer_id_clean"], CUSTOMERS)
    assert first["customer_id_clean"].tolist()[:2] == ["00000123", "12345678"]
    assert pd.isna(first.loc[2, "customer_id_clean"])
    assert not second["customer_id_changed"].any()
    assert second["customer_id_clean"].tolist()[:2] == ["00000123", "12345678"]


def test_many_policy_rows_may_reference_one_customer() -> None:
    result = normalize_customer_ids(pd.Series(["123", "123", "12345678"]), CUSTOMERS)
    assert result["customer_id_clean"].tolist() == ["00000123", "00000123", "12345678"]


def test_duplicate_dimension_keys_are_rejected() -> None:
    dimension = pd.DataFrame({"customer_id": ["00000123", "00000123"]})
    with pytest.raises(DataQualityError, match="duplicate"):
        validate_unique_dimension(dimension, ["customer_id"], name="customers")


def _exposure(start, end, raw, *, strict=True):
    return derive_exposure(
        pd.Series([start]), pd.Series([end]), pd.Series([raw]), strict=strict
    ).iloc[0]


def test_exposure_one_day_and_leap_day_inclusion() -> None:
    one = _exposure(date(2025, 1, 1), date(2025, 1, 1), 0.0027)
    leap = _exposure(date(2024, 2, 28), date(2024, 2, 29), 0.0055)
    assert one["covered_days_inclusive"] == 1
    assert one["exposure_clean"] == pytest.approx(0.0027)
    assert leap["covered_days_inclusive"] == 2
    assert leap["exposure_clean"] == pytest.approx(0.0055)


def test_valid_366_day_period_is_not_capped() -> None:
    result = _exposure(date(2024, 1, 1), date(2024, 12, 31), 1.0027)
    assert result["covered_days_inclusive"] == 366
    assert result["exposure_clean"] == pytest.approx(1.0027)


@pytest.mark.parametrize(
    ("raw", "classification"),
    [(365.0, "stored_day_units"), (365 / 360, "stored_360_basis"), (1.0, "matches_act365")],
)
def test_exposure_classifies_declared_conventions(raw, classification) -> None:
    result = _exposure(date(2023, 1, 1), date(2023, 12, 31), raw)
    assert result["exposure_classification"] == classification
    assert result["exposure_clean"] == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("start", "end", "raw", "message"),
    [(None, date(2025, 1, 1), 1.0, "invalid-date"), (date(2025, 2, 1), date(2025, 1, 1), 1.0, "invalid-date"), (date(2025, 1, 1), date(2025, 1, 2), 99.0, "unresolved")],
)
def test_invalid_or_unresolved_exposure_fails(start, end, raw, message) -> None:
    with pytest.raises(DataQualityError, match=message):
        _exposure(start, end, raw)


def test_exposure_rerun_derives_from_dates_not_prior_clean_value() -> None:
    first = _exposure(date(2023, 1, 1), date(2023, 12, 31), 365.0)
    second = _exposure(date(2023, 1, 1), date(2023, 12, 31), 365.0)
    assert first["exposure_clean"] == second["exposure_clean"] == 1.0


def test_sum_insured_candidate_is_line_specific_reversible_and_idempotent() -> None:
    values = pd.Series([250_000.0, 52_000_000.0, 2_000_000.0, None])
    first = derive_sum_insured_candidate(values, line="buildings", separator=2_000_000)
    second = derive_sum_insured_candidate(values, line="buildings", separator=2_000_000)
    assert first["sum_insured_candidate_status"].tolist() == ["unchanged", "inferred", "ambiguous", "missing"]
    assert first.loc[1, "sum_insured_candidate"] == 52_000.0
    assert first.equals(second)
    contents = derive_sum_insured_candidate(pd.Series([1_500_000.0]), line="contents", separator=1_000_000)
    assert contents.loc[0, "sum_insured_candidate_status"] == "inferred"


def test_telematics_missingness_and_licence_plausibility_remain_flags() -> None:
    source = pd.DataFrame(
        {
            "telematics_opt_in": [False, True, False],
            "telematics_score": [None, None, 0.0],
            "driver_age": [20, 30, 40],
            "years_licensed": [8, 10, 5],
        }
    )
    result = motor_quality_flags(source)
    assert result["telematics_missing_reason"].tolist() == [
        "structural_non_opt_in", "unexpected_opted_in_missing", "unexpected_non_opt_in_score"
    ]
    assert result["licence_start_age_below_14_flag"].tolist() == [True, False, False]
    assert pd.isna(source.loc[0, "telematics_score"])


def test_guarded_join_preserves_order_duplicate_policy_ids_and_null_nonmatch() -> None:
    policies = pd.DataFrame(
        {
            "row_id": ["r2", "r1", "r3"],
            "policy_id": ["p", "p", "q"],
            "customer_id": ["c2", "c1", None],
            "premium": [2.0, 1.0, 3.0],
        }
    )
    dimension = pd.DataFrame({"customer_id": ["c1", "c2"], "segment": ["A", "B"]})
    result = guarded_left_join(policies, dimension.iloc[::-1], left_on=["customer_id"], prefix="customer_")
    assert result["row_id"].tolist() == ["r2", "r1", "r3"]
    assert result["customer_segment"].tolist()[:2] == ["B", "A"]
    assert pd.isna(result.loc[2, "customer_segment"])
    assert result["premium"].sum() == policies["premium"].sum()


def test_weather_join_uses_address_and_year_and_rejects_duplicate_key() -> None:
    policies = pd.DataFrame({"row_id": ["r1", "r2"], "address_id": ["a", "a"], "year": [2024, 2025]})
    weather = pd.DataFrame({"address_id": ["a", "a"], "year": [2024, 2025], "rain": [4.0, 5.0]})
    result = guarded_left_join(policies, weather, left_on=["address_id", "year"], prefix="weather_")
    assert result["weather_rain"].tolist() == [4.0, 5.0]
    duplicate = pd.concat([weather, weather.iloc[[0]]], ignore_index=True)
    with pytest.raises(DataQualityError, match="duplicate"):
        guarded_left_join(policies, duplicate, left_on=["address_id", "year"], prefix="weather_")


def test_cross_year_period_is_detectable_without_selecting_start_year() -> None:
    start = pd.Series(pd.to_datetime(["2024-12-31", "2025-01-01"]))
    end = pd.Series(pd.to_datetime(["2025-01-01", "2025-12-31"]))
    assert start.dt.year.ne(end.dt.year).tolist() == [True, False]
