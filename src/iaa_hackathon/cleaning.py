"""Pure Step 2 cleaning and guarded-join primitives.

Every transformation derives from preserved source values.  The functions do
not construct claims targets, fit estimators, or mutate their inputs.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Collection, Sequence
from typing import Any

import numpy as np
import pandas as pd


class DataQualityError(ValueError):
    """Raised when a declared clean-data invariant is violated."""


def normalize_customer_id(
    value: Any,
    canonical_ids: Collection[str],
    *,
    width: int = 8,
) -> tuple[str | None, bool, str]:
    """Normalize one supported shortened decimal ID without numeric coercion."""
    if value is None or pd.isna(value):
        return None, False, "missing"
    if not isinstance(value, str):
        return None, False, "malformed"
    if value in canonical_ids:
        return value, False, "already_canonical"
    if len(value) > width:
        return None, False, "overlong"
    if not re.fullmatch(r"[0-9]+", value):
        return None, False, "malformed"
    candidate = value.zfill(width)
    if candidate in canonical_ids:
        return candidate, True, "leading_zero_recovered"
    return None, False, "unresolved_reference"


def normalize_customer_ids(
    values: pd.Series,
    canonical_ids: Collection[str],
    *,
    width: int = 8,
) -> pd.DataFrame:
    """Vectorized wrapper retaining raw identifiers and explicit outcomes."""
    raw = values.copy()
    text = raw.astype("string")
    canonical = text.isin(canonical_ids)
    missing = text.isna()
    digit = text.str.fullmatch(r"[0-9]+").fillna(False)
    length = text.str.len()
    overlong = digit & length.gt(width)
    short = digit & length.lt(width)
    padded = text.str.zfill(width)
    repair = short & padded.isin(canonical_ids)
    unresolved = short & ~repair
    malformed = ~missing & ~canonical & ~digit

    clean = pd.Series(pd.NA, index=values.index, dtype="string")
    clean.loc[canonical] = text.loc[canonical]
    clean.loc[repair] = padded.loc[repair]
    reason = pd.Series("unresolved_reference", index=values.index, dtype="string")
    reason.loc[missing] = "missing"
    reason.loc[canonical] = "already_canonical"
    reason.loc[repair] = "leading_zero_recovered"
    reason.loc[overlong] = "overlong"
    reason.loc[malformed] = "malformed"
    reason.loc[unresolved] = "unresolved_reference"
    return pd.DataFrame(
        {
            "customer_id_raw": raw,
            "customer_id_clean": clean,
            "customer_id_changed": repair.astype(bool),
            "customer_id_reason": reason,
        },
        index=values.index,
    )


def derive_exposure(
    period_start: pd.Series,
    period_end: pd.Series,
    exposure_raw: pd.Series,
    *,
    decimals: int = 4,
    absolute_tolerance: float = 0.00005,
    strict: bool = True,
) -> pd.DataFrame:
    """Derive inclusive ACT/365 exposure and classify the supplied value."""
    start = pd.to_datetime(period_start, errors="coerce")
    end = pd.to_datetime(period_end, errors="coerce")
    raw = pd.to_numeric(exposure_raw, errors="coerce")
    valid_dates = start.notna() & end.notna() & end.ge(start)
    days = (end - start).dt.days.add(1).where(valid_dates)
    clean = days.div(365).round(decimals)

    def close(left: pd.Series, right: pd.Series) -> pd.Series:
        result = np.isclose(
            left.to_numpy(dtype=float, na_value=np.nan),
            right.to_numpy(dtype=float, na_value=np.nan),
            atol=absolute_tolerance,
            rtol=0,
            equal_nan=False,
        )
        return pd.Series(result, index=left.index)

    match = valid_dates & close(raw, clean)
    day_units = valid_dates & ~match & close(raw, days.astype(float))
    basis_360 = valid_dates & ~match & ~day_units & close(raw, days.div(360).round(decimals))
    unresolved = valid_dates & ~(match | day_units | basis_360)
    invalid = ~valid_dates
    if strict and (invalid.any() or unresolved.any()):
        raise DataQualityError(
            "exposure reconciliation failed: "
            f"{int(invalid.sum())} invalid-date rows and "
            f"{int(unresolved.sum())} unresolved mismatches"
        )

    classification = pd.Series("unresolved_mismatch", index=raw.index, dtype="string")
    classification.loc[match] = "matches_act365"
    classification.loc[day_units] = "stored_day_units"
    classification.loc[basis_360] = "stored_360_basis"
    classification.loc[invalid] = "invalid_dates"
    reason = classification.map(
        {
            "matches_act365": "raw_matches_inclusive_act365",
            "stored_day_units": "raw_stored_inclusive_days",
            "stored_360_basis": "raw_matches_inclusive_days_over_360",
            "unresolved_mismatch": "raw_value_not_explained_by_declared_rules",
            "invalid_dates": "missing_or_inverted_coverage_dates",
        }
    ).astype("string")
    return pd.DataFrame(
        {
            "exposure_raw": exposure_raw.copy(),
            "exposure_clean": clean,
            "exposure_classification": classification,
            "exposure_changed": (valid_dates & ~match).astype(bool),
            "exposure_reason": reason,
            "covered_days_inclusive": days.astype("Int64"),
        },
        index=exposure_raw.index,
    )


def derive_sum_insured_candidate(
    values: pd.Series,
    *,
    line: str,
    separator: float,
    divisor: float = 1000.0,
) -> pd.DataFrame:
    """Create, but do not canonically adopt, the supported unit candidate."""
    raw = pd.to_numeric(values, errors="coerce")
    missing = raw.isna()
    inferred = raw.gt(separator)
    boundary = raw.eq(separator)
    candidate = raw.copy()
    candidate.loc[inferred] = raw.loc[inferred].div(divisor)
    status = pd.Series("unchanged", index=values.index, dtype="string")
    status.loc[missing] = "missing"
    status.loc[boundary] = "ambiguous"
    status.loc[inferred] = "inferred"
    reason = pd.Series(
        f"below_{line}_diagnostic_gap_separator",
        index=values.index,
        dtype="string",
    )
    reason.loc[missing] = "source_value_missing"
    reason.loc[boundary] = "at_diagnostic_separator_requires_review"
    reason.loc[inferred] = "high_cluster_factor_1000_candidate"
    flag = pd.Series(False, index=values.index, dtype="boolean")
    flag.loc[missing | boundary] = pd.NA
    flag.loc[inferred] = True
    proposed = pd.Series(np.nan, index=values.index, dtype=float)
    proposed.loc[inferred] = divisor
    return pd.DataFrame(
        {
            "sum_insured_raw": values.copy(),
            "sum_insured_candidate": candidate,
            "sum_insured_unit_error_flag": flag,
            "sum_insured_proposed_divisor": proposed,
            "sum_insured_candidate_reason": reason,
            "sum_insured_candidate_status": status,
        },
        index=values.index,
    )


def motor_quality_flags(frame: pd.DataFrame) -> pd.DataFrame:
    """Separate structural telematics absence and subjective licence-age flags."""
    opt_in = frame["telematics_opt_in"].astype("boolean")
    score_missing = frame["telematics_score"].isna()
    reason = pd.Series("score_present", index=frame.index, dtype="string")
    reason.loc[~opt_in.fillna(False) & score_missing] = "structural_non_opt_in"
    reason.loc[opt_in.fillna(False) & score_missing] = "unexpected_opted_in_missing"
    reason.loc[~opt_in.fillna(False) & ~score_missing] = "unexpected_non_opt_in_score"
    reason.loc[opt_in.isna()] = "unknown_opt_in_status"
    licence_start_age = frame["driver_age"] - frame["years_licensed"]
    return pd.DataFrame(
        {
            "telematics_score_missing": score_missing.astype(bool),
            "telematics_missing_reason": reason,
            "licence_start_age_derived": licence_start_age,
            "licence_start_age_below_14_flag": licence_start_age.lt(14).fillna(False),
        },
        index=frame.index,
    )


def validate_unique_dimension(
    dimension: pd.DataFrame,
    keys: Sequence[str],
    *,
    name: str,
) -> None:
    """Require non-null, unique dimension keys at the declared grain."""
    missing = dimension.loc[:, list(keys)].isna().any(axis=1)
    duplicate = dimension.loc[:, list(keys)].duplicated(keep=False)
    if missing.any() or duplicate.any():
        raise DataQualityError(
            f"{name} key validation failed: {int(missing.sum())} null-key rows and "
            f"{int(duplicate.sum())} rows participating in duplicate keys"
        )


def guarded_left_join(
    policies: pd.DataFrame,
    dimension: pd.DataFrame,
    *,
    left_on: Sequence[str],
    right_on: Sequence[str] | None = None,
    row_id: str = "row_id",
    prefix: str = "dimension_",
) -> pd.DataFrame:
    """Many-to-one left join that never permits null-to-null key matching."""
    right_on = tuple(right_on or left_on)
    left_on = tuple(left_on)
    validate_unique_dimension(dimension, right_on, name=prefix.rstrip("_") or "dimension")
    if row_id not in policies:
        raise DataQualityError(f"policy frame is missing {row_id}")
    before_ids = Counter(policies[row_id].tolist())
    original_columns = set(policies.columns)
    payload = [column for column in dimension.columns if column not in right_on]
    renamed = dimension.rename(columns={column: f"{prefix}{column}" for column in payload})

    working = policies.copy()
    working["__join_order"] = np.arange(len(working))
    null_key = working.loc[:, list(left_on)].isna().any(axis=1)
    nonnull = working.loc[~null_key].merge(
        renamed,
        how="left",
        left_on=list(left_on),
        right_on=list(right_on),
        validate="many_to_one",
        sort=False,
    )
    if tuple(left_on) != tuple(right_on):
        nonnull = nonnull.drop(columns=[key for key in right_on if key not in original_columns])
    null_rows = working.loc[null_key].copy()
    for column in payload:
        null_rows[f"{prefix}{column}"] = pd.NA
    joined = (
        pd.concat([nonnull, null_rows], ignore_index=True, sort=False)
        if not null_rows.empty
        else nonnull
    )
    joined = joined.sort_values("__join_order", kind="stable").drop(columns="__join_order")
    joined.index = policies.index
    if len(joined) != len(policies) or Counter(joined[row_id].tolist()) != before_ids:
        raise DataQualityError("guarded join changed policy row count or row_id multiset")
    return joined
