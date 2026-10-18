"""Claim linkage, observed-response accounting, and transparent scenarios."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd


class ClaimTargetError(ValueError):
    """Raised when claim-target construction would be ambiguous or lossy."""


CLAIM_COLUMNS = [
    "claim_id", "policy_id", "line", "peril", "loss_date", "report_date",
    "status", "paid_to_date", "incurred_to_date", "recoveries",
]


def validate_claims(claims: pd.DataFrame, cutoff: str | pd.Timestamp) -> None:
    missing = sorted(set(CLAIM_COLUMNS).difference(claims.columns))
    if missing:
        raise ClaimTargetError(f"claims missing required columns: {missing}")
    if claims["claim_id"].isna().any() or not claims["claim_id"].is_unique:
        raise ClaimTargetError("claim_id must be unique and non-null")
    loss = pd.to_datetime(claims["loss_date"], errors="coerce")
    report = pd.to_datetime(claims["report_date"], errors="coerce")
    if loss.isna().any() or report.isna().any():
        raise ClaimTargetError("loss_date and report_date must be valid and non-null")
    if report.lt(loss).any():
        raise ClaimTargetError("report_date before loss_date")
    if report.gt(pd.Timestamp(cutoff)).any():
        raise ClaimTargetError("report_date after as-of cutoff")
    for column in ["paid_to_date", "incurred_to_date", "recoveries"]:
        values = pd.to_numeric(claims[column], errors="coerce")
        if values.isna().any() or (values < 0).any():
            raise ClaimTargetError(f"{column} must be finite and nonnegative")
        if not np.isfinite(values).all():
            raise ClaimTargetError(f"{column} must be finite")
        if not np.allclose(values * 100, np.rint(values * 100), atol=1e-6):
            raise ClaimTargetError(f"{column} contains values beyond two-decimal precision")
    case = claims["incurred_to_date"] - claims["paid_to_date"]
    if (case < -1e-8).any():
        raise ClaimTargetError("incurred_to_date is below paid_to_date")


def policy_catalog(policies: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for expected_line, source in policies.items():
        required = {"row_id", "policy_id", "period_start", "period_end", "line", "split"}
        missing = sorted(required.difference(source.columns))
        if missing:
            raise ClaimTargetError(f"{expected_line} policies missing columns: {missing}")
        part = source[["row_id", "policy_id", "period_start", "period_end", "line", "split"]].copy()
        if not part["line"].eq(expected_line).all() or not part["split"].eq("train").all():
            raise ClaimTargetError(f"{expected_line} policy line/split identity failed")
        parts.append(part)
    result = pd.concat(parts, ignore_index=True)
    if result["row_id"].isna().any() or not result["row_id"].is_unique:
        raise ClaimTargetError("training row_id must be unique and non-null across lines")
    result["period_start"] = pd.to_datetime(result["period_start"], errors="coerce")
    result["period_end"] = pd.to_datetime(result["period_end"], errors="coerce")
    if result[["period_start", "period_end"]].isna().any().any():
        raise ClaimTargetError("policy periods contain invalid dates")
    if result["period_end"].lt(result["period_start"]).any():
        raise ClaimTargetError("policy period_end precedes period_start")
    return result


def validate_policy_periods(catalog: pd.DataFrame) -> None:
    ordered = catalog.sort_values(["line", "policy_id", "period_start", "period_end"])
    previous_end = ordered.groupby(["line", "policy_id"], sort=False)["period_end"].shift()
    overlap = previous_end.notna() & ordered["period_start"].le(previous_end)
    if overlap.any():
        examples = ordered.loc[overlap, ["line", "policy_id", "row_id"]].head(5).to_dict("records")
        raise ClaimTargetError(f"overlapping policy periods: {examples}")


def build_claim_crosswalk(
    claims: pd.DataFrame,
    policies: Mapping[str, pd.DataFrame],
    *,
    cutoff: str | pd.Timestamp,
    source_claims_sha256: str,
    strict: bool = True,
) -> pd.DataFrame:
    """Link by exact line/policy and inclusive loss-date coverage."""
    if strict:
        validate_claims(claims, cutoff)
    catalog = policy_catalog(policies)
    if strict:
        validate_policy_periods(catalog)

    base = claims[CLAIM_COLUMNS].copy().reset_index(drop=True)
    base["_claim_order"] = np.arange(len(base), dtype=np.int64)
    base["loss_date"] = pd.to_datetime(base["loss_date"], errors="coerce")
    base["report_date"] = pd.to_datetime(base["report_date"], errors="coerce")
    valid_lines = set(policies)
    exact_keys = catalog[["line", "policy_id"]].drop_duplicates()
    key_groups = catalog.groupby(["line", "policy_id"], sort=False).agg(
        first_start=("period_start", "min"), last_end=("period_end", "max")
    )

    candidates = base.merge(
        catalog[["line", "policy_id", "row_id", "period_start", "period_end"]],
        on=["line", "policy_id"], how="left", sort=False,
    )
    covered = (
        candidates["row_id"].notna()
        & candidates["loss_date"].notna()
        & candidates["loss_date"].ge(candidates["period_start"])
        & candidates["loss_date"].le(candidates["period_end"])
    )
    matches = candidates.loc[covered, ["_claim_order", "row_id"]]
    counts = matches.groupby("_claim_order", sort=False).size()
    one_rows = matches.drop_duplicates("_claim_order").set_index("_claim_order")["row_id"]

    result = base.copy()
    result["match_count"] = result["_claim_order"].map(counts).fillna(0).astype("int64")
    result["matched_row_id"] = result["_claim_order"].map(one_rows).where(result["match_count"].eq(1))
    result["disposition"] = np.select(
        [result["match_count"].eq(1), result["match_count"].gt(1)],
        ["exactly_one_match", "ambiguous_multiple_match"], default="unmatched",
    )

    keys = pd.MultiIndex.from_frame(result[["line", "policy_id"]])
    known_keys = pd.MultiIndex.from_frame(exact_keys)
    has_exact_key = pd.Series(keys.isin(known_keys), index=result.index)
    bounds = key_groups.reindex(keys)
    bounds.index = result.index
    reason = pd.Series(pd.NA, index=result.index, dtype="string")
    unmatched = result["match_count"].eq(0)
    reason.loc[unmatched & ~result["line"].isin(valid_lines)] = "unknown_line"
    reason.loc[unmatched & result["line"].isin(valid_lines) & ~has_exact_key] = "unknown_policy"
    reason.loc[unmatched & result["loss_date"].isna()] = "invalid_or_missing_loss_date"
    eligible = unmatched & has_exact_key & result["loss_date"].notna()
    reason.loc[eligible & result["loss_date"].lt(bounds["first_start"])] = "before_first_supplied_coverage"
    reason.loc[eligible & result["loss_date"].gt(bounds["last_end"])] = "after_last_supplied_coverage"
    reason.loc[eligible & reason.isna()] = "between_supplied_periods"
    reason.loc[result["match_count"].gt(1)] = "overlapping_coverage"
    reason.loc[unmatched & reason.isna()] = "other_explicit_cause"
    result["exception_reason"] = reason
    result["linkage_rule_version"] = "step3-target-construction-v1"
    result["source_claims_sha256"] = source_claims_sha256
    result["as_of_cutoff"] = pd.Timestamp(cutoff)
    result = result.drop(columns="_claim_order")
    if len(result) != len(claims):
        raise ClaimTargetError("crosswalk does not preserve one record per source claim")
    return result


def add_observed_components(
    crosswalk: pd.DataFrame,
    *,
    accepted_statuses: tuple[str, ...] = ("closed", "open"),
    excluded_statuses: tuple[str, ...] = ("repudiated",),
) -> pd.DataFrame:
    result = crosswalk.copy()
    known = set(accepted_statuses) | set(excluded_statuses)
    unknown = sorted(set(result["status"].dropna().unique()).difference(known))
    if unknown:
        raise ClaimTargetError(f"unknown claim statuses: {unknown}")
    result["accepted_for_observed"] = (
        result["disposition"].eq("exactly_one_match") & result["status"].isin(accepted_statuses)
    )
    result["case_reserve"] = result["incurred_to_date"] - result["paid_to_date"]
    result["observed_net_incurred"] = result["incurred_to_date"] - result["recoveries"]
    accepted = result["accepted_for_observed"]
    if (result.loc[accepted, "observed_net_incurred"] < -1e-8).any():
        raise ClaimTargetError("negative observed net incurred; financial basis requires investigation")
    return result


def build_observed_response(
    crosswalk: pd.DataFrame,
    policies: Mapping[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    enriched = add_observed_components(crosswalk)
    accepted = enriched.loc[enriched["accepted_for_observed"]].copy()
    accepted["positive_observed_cost"] = accepted["observed_net_incurred"].gt(0).astype("int64")
    value_columns = ["paid_to_date", "incurred_to_date", "case_reserve", "recoveries", "observed_net_incurred"]
    row_agg = accepted.groupby(["matched_row_id", "line"], sort=False).agg(
        accepted_reported_claim_count=("claim_id", "size"),
        positive_observed_cost_claim_count=("positive_observed_cost", "sum"),
        **{column: (column, "sum") for column in value_columns},
    ).reset_index().rename(columns={"matched_row_id": "row_id", "recoveries": "observed_recoveries"})
    peril_agg = accepted.groupby(["matched_row_id", "line", "peril"], sort=False).agg(
        accepted_reported_claim_count=("claim_id", "size"),
        positive_observed_cost_claim_count=("positive_observed_cost", "sum"),
        **{column: (column, "sum") for column in value_columns},
    ).reset_index().rename(columns={"matched_row_id": "row_id", "recoveries": "observed_recoveries"})

    policy_parts = []
    for line, frame in policies.items():
        part = frame[["row_id", "line", "period_start", "period_end", "exposure_raw", "exposure_clean"]].copy()
        if not part["line"].eq(line).all():
            raise ClaimTargetError(f"policy line mismatch for {line}")
        policy_parts.append(part)
    all_rows = pd.concat(policy_parts, ignore_index=True)
    response = all_rows.merge(row_agg, on=["row_id", "line"], how="left", validate="one_to_one", sort=False)
    count_cols = ["accepted_reported_claim_count", "positive_observed_cost_claim_count"]
    response[count_cols] = response[count_cols].fillna(0).astype("int64")
    amount_cols = ["paid_to_date", "incurred_to_date", "case_reserve", "observed_recoveries", "observed_net_incurred"]
    response[amount_cols] = response[amount_cols].fillna(0.0)
    if len(response) != len(all_rows) or not response["row_id"].is_unique:
        raise ClaimTargetError("observed response did not preserve policy-row identity")
    return response, peril_agg


def apply_reported_claim_scenario(
    claims: pd.DataFrame,
    *,
    case_multiplier: float,
    future_recovery: float | pd.Series = 0.0,
) -> pd.Series:
    if not np.isfinite(case_multiplier) or case_multiplier < 0:
        raise ClaimTargetError("case_multiplier must be finite and nonnegative")
    recovery = pd.Series(future_recovery, index=claims.index, dtype="float64")
    if recovery.isna().any() or (~np.isfinite(recovery)).any() or (recovery < 0).any():
        raise ClaimTargetError("future recovery must be finite and nonnegative")
    case = claims["incurred_to_date"] - claims["paid_to_date"]
    result = claims["paid_to_date"] + case_multiplier * case - claims["recoveries"] - recovery
    if (result < -1e-8).any():
        raise ClaimTargetError("scenario creates negative net claim amount; no clipping applied")
    return result


def monetary_reconciliation(crosswalk: pd.DataFrame) -> dict[str, Any]:
    fields = ["paid_to_date", "incurred_to_date", "recoveries"]
    groups: dict[str, Any] = {}
    for name, part in crosswalk.groupby("disposition", dropna=False):
        groups[str(name)] = {"claim_count": int(len(part)), **{f"{f}_minor_units": int(np.rint(part[f] * 100).sum()) for f in fields}}
    return {
        "source": {"claim_count": int(len(crosswalk)), **{f"{f}_minor_units": int(np.rint(crosswalk[f] * 100).sum()) for f in fields}},
        "by_disposition": groups,
    }
