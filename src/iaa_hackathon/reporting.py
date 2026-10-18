"""Auditable right-truncated reporting-delay diagnostics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from iaa_hackathon.claim_targets import ClaimTargetError


@dataclass(frozen=True)
class GeometricDelayFit:
    line: str
    peril: str
    probability: float
    claim_count: int
    max_observed_delay_days: int
    fit_report_cutoff: str
    fit_population: str = "exactly matched claims reported by cutoff; no final-status exclusion"
    estimation_scope: str = "full_snapshot_diagnostic_not_fold_safe"
    family: str = "discrete_geometric_days"
    converged: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def geometric_cdf(age_days: np.ndarray | pd.Series | int, probability: float) -> np.ndarray:
    if not 0 < probability <= 1:
        raise ClaimTargetError("geometric probability must be in (0, 1]")
    age = np.floor(np.asarray(age_days, dtype=float)).astype(int)
    result = np.zeros(age.shape, dtype=float)
    valid = age >= 0
    result[valid] = -np.expm1((age[valid] + 1) * np.log1p(-probability)) if probability < 1 else 1.0
    return result


def _negative_log_likelihood(probability: float, delay: np.ndarray, age: np.ndarray) -> float:
    if not 0 < probability < 1:
        return np.inf
    log_q = np.log1p(-probability)
    log_f = np.log(probability) + delay * log_q
    # log(1 - q^(age+1)), written stably for old and very recent occurrences.
    log_F = np.log(-np.expm1((age + 1) * log_q))
    value = -float(np.sum(log_f - log_F))
    return value if np.isfinite(value) else np.inf


def fit_geometric_delay(
    claims: pd.DataFrame,
    *,
    cutoff: str | pd.Timestamp,
    line: str,
    peril: str,
    min_claims: int = 30,
    estimation_scope: str = "full_snapshot_diagnostic_not_fold_safe",
) -> GeometricDelayFit:
    cutoff_ts = pd.Timestamp(cutoff)
    loss = pd.to_datetime(claims["loss_date"])
    report = pd.to_datetime(claims["report_date"])
    visible = claims.loc[loss.le(cutoff_ts) & report.le(cutoff_ts)].copy()
    delay = (pd.to_datetime(visible["report_date"]) - pd.to_datetime(visible["loss_date"])).dt.days.to_numpy()
    age = (cutoff_ts - pd.to_datetime(visible["loss_date"])).dt.days.to_numpy()
    if len(delay) < min_claims:
        raise ClaimTargetError(f"sparse reporting-delay group {line}/{peril}: {len(delay)} < {min_claims}")
    if (delay < 0).any() or (delay > age).any():
        raise ClaimTargetError("delay sample violates 0 <= D <= A at fit cutoff")
    result = minimize_scalar(
        _negative_log_likelihood,
        bounds=(1e-8, 1 - 1e-10),
        args=(delay.astype(float), age.astype(float)),
        method="bounded",
        options={"xatol": 1e-12, "maxiter": 1000},
    )
    if not result.success or not np.isfinite(result.fun):
        raise ClaimTargetError(f"reporting-delay optimization failed for {line}/{peril}: {result.message}")
    return GeometricDelayFit(
        line=line,
        peril=peril,
        probability=float(result.x),
        claim_count=int(len(delay)),
        max_observed_delay_days=int(delay.max(initial=0)),
        fit_report_cutoff=cutoff_ts.date().isoformat(),
        estimation_scope=estimation_scope,
        converged=bool(result.success),
    )


def fit_reporting_groups(
    claims: pd.DataFrame,
    *,
    cutoff: str | pd.Timestamp,
    min_claims: int = 30,
    estimation_scope: str = "full_snapshot_diagnostic_not_fold_safe",
) -> dict[tuple[str, str], GeometricDelayFit]:
    fits: dict[tuple[str, str], GeometricDelayFit] = {}
    for (line, peril), part in claims.groupby(["line", "peril"], sort=True):
        fits[(str(line), str(peril))] = fit_geometric_delay(
            part, cutoff=cutoff, line=str(line), peril=str(peril), min_claims=min_claims,
            estimation_scope=estimation_scope,
        )
    return fits


def average_period_completeness(
    period_start: pd.Series,
    period_end: pd.Series,
    *,
    cutoff: str | pd.Timestamp,
    probability: float,
) -> np.ndarray:
    """Average F(age) over inclusive covered dates under uniform daily incidence."""
    cutoff_ts = pd.Timestamp(cutoff)
    start = pd.to_datetime(period_start)
    end = pd.to_datetime(period_end).clip(upper=cutoff_ts)
    if start.isna().any() or end.isna().any() or end.lt(start).any():
        raise ClaimTargetError("period dates are invalid at transform cutoff")
    maximum_age = int((cutoff_ts - start.min()).days)
    lookup = geometric_cdf(np.arange(maximum_age + 1), probability)
    prefix = np.concatenate([[0.0], np.cumsum(lookup)])
    youngest = (cutoff_ts - end).dt.days.to_numpy(dtype=int)
    oldest = (cutoff_ts - start).dt.days.to_numpy(dtype=int)
    total = prefix[oldest + 1] - prefix[youngest]
    count = oldest - youngest + 1
    result = total / count
    if (~np.isfinite(result)).any() or (result < -1e-12).any() or (result > 1 + 1e-12).any():
        raise ClaimTargetError("invalid period completeness")
    # Prefix-sum subtraction can exceed one by a few floating-point ulps.
    return np.clip(result, 0.0, 1.0)


def finite_followup_backtest(
    claims: pd.DataFrame,
    *,
    fit_cutoff: str | pd.Timestamp,
    followup_cutoff: str | pd.Timestamp,
    min_claims: int = 30,
) -> list[dict[str, Any]]:
    fit_cutoff_ts = pd.Timestamp(fit_cutoff)
    followup_ts = pd.Timestamp(followup_cutoff)
    eligible = claims.loc[pd.to_datetime(claims["loss_date"]).le(fit_cutoff_ts)].copy()
    results: list[dict[str, Any]] = []
    for (line, peril), group in eligible.groupby(["line", "peril"], sort=True):
        seen = group.loc[pd.to_datetime(group["report_date"]).le(fit_cutoff_ts)]
        if len(seen) < min_claims:
            results.append({
                "line": str(line), "peril": str(peril), "fit_cutoff": fit_cutoff_ts.date().isoformat(),
                "status": "unavailable_sparse", "seen_at_fit": int(len(seen)), "min_claims": min_claims,
            })
            continue
        fit = fit_geometric_delay(
            group, cutoff=fit_cutoff_ts, line=str(line), peril=str(peril), min_claims=min_claims,
            estimation_scope="historical_cutoff_finite_followup_backtest",
        )
        age = (fit_cutoff_ts - pd.to_datetime(seen["loss_date"])).dt.days.to_numpy()
        completeness = geometric_cdf(age, fit.probability)
        if (completeness <= 0).any():
            raise ClaimTargetError("zero fitted completeness in backtest; no silent flooring")
        predicted = float(np.sum(1.0 / completeness))
        actual = int((pd.to_datetime(group["report_date"]) <= followup_ts).sum())
        results.append({
            "line": str(line), "peril": str(peril), "fit_cutoff": fit_cutoff_ts.date().isoformat(),
            "followup_cutoff": followup_ts.date().isoformat(), "status": "available",
            "seen_at_fit": int(len(seen)), "predicted_reported_by_unbounded_tail": predicted,
            "actually_reported_by_finite_followup": actual,
            "count_error": predicted - actual,
            "probability": fit.probability,
            "limitation": "final available count is finite follow-up, not ultimate",
        })
    return results
