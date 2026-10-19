"""Assumption-dependent Bornhuetter-Ferguson-style unreported-loss bridge.

This is an *estimate*, not an observed ultimate label.  Existing observed-response
and frozen Step 9 assets are intentionally never modified by this module.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from iaa_hackathon.reporting import average_period_completeness


def bridge_response(
    policies: pd.DataFrame,
    claims: pd.DataFrame,
    probabilities: dict[tuple[str, str], float],
    *,
    mature_rate_years: tuple[int, ...],
    rate_cutoff: str,
    valuation_date: str,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Return observed + expected IBNR per policy, with training-only peril rates.

    Rate = mature claims reported by ``rate_cutoff`` / effective mature
    exposure at that cutoff.  IBNR = rate * exposure * (1 - reporting CDF).
    The known claim component remains valued at ``valuation_date``; historical
    financial snapshots do not exist, so historical folds are retrospective.
    """
    required_policy = {"row_id", "line", "period_start", "period_end", "exposure_clean", "observed_net_incurred"}
    required_claim = {"matched_row_id", "line", "peril", "report_date", "accepted_for_observed", "observed_net_incurred"}
    if required_policy - set(policies) or required_claim - set(claims):
        raise ValueError("bridge input is missing required fields")
    if policies.row_id.isna().any() or policies.row_id.duplicated().any():
        raise ValueError("policy row_id must be unique and non-null")
    exposure = policies.exposure_clean.to_numpy(dtype=float)
    observed = policies.observed_net_incurred.to_numpy(dtype=float)
    if not np.isfinite(exposure).all() or (exposure <= 0).any() or not np.isfinite(observed).all() or (observed < 0).any():
        raise ValueError("invalid exposure or observed net incurred")
    if pd.Timestamp(rate_cutoff) > pd.Timestamp(valuation_date):
        raise ValueError("rate cutoff cannot exceed valuation date")
    years = pd.to_datetime(policies.period_start).dt.year
    mature = years.isin(mature_rate_years)
    if not mature.any() or not set(mature_rate_years).issubset(set(years)):
        raise ValueError("mature rate years are absent from policy input")
    if (pd.to_datetime(policies.period_end) > pd.Timestamp(valuation_date)).any():
        raise ValueError("policy period extends past financial valuation")
    if (pd.to_datetime(policies.loc[mature, "period_end"]) > pd.Timestamp(rate_cutoff)).any():
        raise ValueError("mature rate policy extends past rate cutoff")
    accepted = claims.loc[claims.accepted_for_observed].copy()
    if accepted.matched_row_id.isna().any() or (accepted.observed_net_incurred < 0).any():
        raise ValueError("invalid accepted claim universe")
    if not set(accepted.matched_row_id).issubset(set(policies.row_id)):
        raise ValueError("accepted claims do not belong to the supplied policy universe")
    per_row_claim = accepted.groupby("matched_row_id").observed_net_incurred.sum()
    if not np.allclose(policies.row_id.map(per_row_claim).fillna(0).to_numpy(float), observed, rtol=0, atol=1e-6):
        raise ValueError("known claim amounts do not reconcile to policy response")
    expected_groups = set(accepted[["line", "peril"]].itertuples(index=False, name=None))
    if expected_groups != set(probabilities):
        raise ValueError("reporting fit groups differ from the accepted claim universe")
    if any(not np.isfinite(p) or not 0 < p <= 1 for p in probabilities.values()):
        raise ValueError("invalid reporting probability")

    rate_claims = accepted.loc[
        accepted.matched_row_id.isin(policies.loc[mature, "row_id"])
        & pd.to_datetime(accepted.report_date).le(pd.Timestamp(rate_cutoff))
    ]
    rate_amounts = rate_claims.groupby(["line", "peril"]).observed_net_incurred.sum()
    ibnr = np.zeros(len(policies), dtype=float)
    diagnostics: list[dict[str, Any]] = []
    for line, peril in sorted(probabilities):
        line_mask = policies.line.eq(line).to_numpy()
        mature_line = line_mask & mature.to_numpy()
        if not mature_line.any() or not line_mask.any():
            raise ValueError(f"missing policy population for {line}/{peril}")
        p = probabilities[(line, peril)]
        mature_part = policies.loc[mature_line]
        c_rate = average_period_completeness(
            mature_part.period_start, mature_part.period_end, cutoff=rate_cutoff, probability=p
        )
        effective_exposure = float(np.dot(mature_part.exposure_clean.to_numpy(float), c_rate))
        mature_cost = float(rate_amounts.get((line, peril), 0.0))
        if effective_exposure <= 0 or mature_cost <= 0:
            raise ValueError(f"no estimable mature positive cost rate for {line}/{peril}")
        rate = mature_cost / effective_exposure
        part = policies.loc[line_mask]
        c_valuation = average_period_completeness(
            part.period_start, part.period_end, cutoff=valuation_date, probability=p
        )
        addition = rate * part.exposure_clean.to_numpy(float) * (1 - c_valuation)
        if not np.isfinite(addition).all() or (addition < -1e-8).any():
            raise ValueError("invalid monetary IBNR estimate")
        ibnr[line_mask] += addition
        diagnostics.append({
            "line": line, "peril": peril, "delay_probability": p,
            "mature_reported_cost": mature_cost,
            "mature_effective_exposure": effective_exposure,
            "estimated_mature_cost_rate": rate,
            "policy_rows": int(line_mask.sum()),
            "mean_reporting_completeness_at_valuation": float(np.mean(c_valuation)),
            "estimated_unreported_cost": float(addition.sum()),
        })
    result = policies[["row_id", "line"]].copy()
    result["observed_net_incurred"] = observed
    result["estimated_unreported_net_cost"] = ibnr
    result["conditional_ultimate_net_cost"] = observed + ibnr
    if not np.isfinite(result.conditional_ultimate_net_cost).all() or (result.conditional_ultimate_net_cost < 0).any():
        raise ValueError("invalid conditional ultimate response")
    return result, diagnostics
