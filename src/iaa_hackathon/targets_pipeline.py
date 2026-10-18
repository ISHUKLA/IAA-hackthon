"""Atomic Step 3 target-construction pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import scipy

from iaa_hackathon.claim_targets import (
    ClaimTargetError,
    add_observed_components,
    apply_reported_claim_scenario,
    build_claim_crosswalk,
    build_observed_response,
    monetary_reconciliation,
)
from iaa_hackathon.prepare import sha256_file
from iaa_hackathon.reporting import (
    average_period_completeness,
    finite_followup_backtest,
    fit_reporting_groups,
)


POLICY_COLUMNS = [
    "row_id", "policy_id", "period_start", "period_end", "exposure_raw",
    "exposure_clean", "line", "split",
]


def _minor(value: pd.Series) -> int:
    return int(np.rint(value.to_numpy(dtype=float) * 100).sum())


def _json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def _read_inputs(
    data_dir: Path, step2_dir: Path, config: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, Any]]:
    manifest_path = step2_dir / "prepare-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    expected_digest = config["inputs"]["clean_training_policies"]["manifest_logical_output_digest"]
    if manifest.get("logical_output_digest") != expected_digest:
        raise ClaimTargetError("Step 2 manifest logical digest differs from target configuration")
    if manifest.get("status") != "complete" or not manifest.get("raw_hashes_unchanged"):
        raise ClaimTargetError("Step 2 manifest is not a complete immutable build")
    claims_path = data_dir / "claims.parquet"
    expected_claim_hash = config["inputs"]["claims"]["reference_sha256"]
    if sha256_file(claims_path) != expected_claim_hash:
        raise ClaimTargetError("claims.parquet hash mismatch")
    claims = pd.read_parquet(claims_path, columns=config["inputs"]["claims"]["required_columns"])
    policies: dict[str, pd.DataFrame] = {}
    for line, relative in config["inputs"]["clean_training_policies"]["files"].items():
        path = Path(relative)
        if not path.is_absolute():
            path = Path.cwd() / path
        manifest_relative = str(path.relative_to(step2_dir))
        if sha256_file(path) != manifest["outputs"].get(manifest_relative):
            raise ClaimTargetError(f"Step 2 clean output hash mismatch: {manifest_relative}")
        policies[line] = pd.read_parquet(path, columns=POLICY_COLUMNS)
    return claims, policies, manifest


def _maturity_diagnostics(claims: pd.DataFrame, cutoff: pd.Timestamp) -> dict[str, Any]:
    data = claims.copy()
    data["reporting_delay_days"] = (pd.to_datetime(data["report_date"]) - pd.to_datetime(data["loss_date"])).dt.days
    data["maximum_observable_delay_days"] = (cutoff - pd.to_datetime(data["loss_date"])).dt.days
    data["case_reserve"] = data["incurred_to_date"] - data["paid_to_date"]
    data["loss_year"] = pd.to_datetime(data["loss_date"]).dt.year
    data["loss_month"] = pd.to_datetime(data["loss_date"]).dt.to_period("M").astype(str)
    data["report_month"] = pd.to_datetime(data["report_date"]).dt.to_period("M").astype(str)
    data["claim_age_band"] = pd.cut(
        data["maximum_observable_delay_days"],
        bins=[-1, 30, 90, 180, 365, 730, np.inf],
        labels=["0-30", "31-90", "91-180", "181-365", "366-730", "731+"],
    ).astype("string")
    data["open_claim"] = data["status"].eq("open")
    data["open_incurred"] = data["incurred_to_date"].where(data["open_claim"], 0.0)

    def summarize(keys: list[str]) -> list[dict[str, Any]]:
        grouped = data.groupby(keys, dropna=False, sort=True)
        rows = grouped.agg(
            claim_count=("claim_id", "size"), open_claim_count=("open_claim", "sum"),
            paid=("paid_to_date", "sum"), incurred=("incurred_to_date", "sum"),
            case_reserve=("case_reserve", "sum"), recoveries=("recoveries", "sum"),
            open_incurred=("open_incurred", "sum"), mean_delay_days=("reporting_delay_days", "mean"),
            p95_delay_days=("reporting_delay_days", lambda x: float(x.quantile(0.95))),
            max_delay_days=("reporting_delay_days", "max"),
        ).reset_index()
        rows["open_claim_count_share"] = rows["open_claim_count"] / rows["claim_count"]
        rows["open_incurred_share"] = np.divide(
            rows["open_incurred"], rows["incurred"], out=np.zeros(len(rows)), where=rows["incurred"].ne(0)
        )
        return rows.to_dict("records")

    largest = data.nlargest(20, "incurred_to_date")[[
        "claim_id", "line", "peril", "loss_date", "report_date", "status",
        "paid_to_date", "incurred_to_date", "case_reserve", "recoveries",
    ]].copy()
    for column in ["loss_date", "report_date"]:
        largest[column] = pd.to_datetime(largest[column]).dt.date.astype(str)
    return {
        "valuation_date": cutoff.date().isoformat(),
        "population": "exactly matched accepted claims only",
        "invalid_negative_reporting_delay_count": int(data["reporting_delay_days"].lt(0).sum()),
        "reports_after_cutoff_count": int(pd.to_datetime(data["report_date"]).gt(cutoff).sum()),
        "delay_tail": {
            "maximum_days": int(data["reporting_delay_days"].max()),
            "over_30_days_count": int(data["reporting_delay_days"].gt(30).sum()),
            "over_90_days_count": int(data["reporting_delay_days"].gt(90).sum()),
            "over_365_days_count": int(data["reporting_delay_days"].gt(365).sum()),
        },
        "by_line_peril": summarize(["line", "peril"]),
        "by_line_loss_year": summarize(["line", "loss_year"]),
        "by_line_claim_age_band": summarize(["line", "claim_age_band"]),
        "by_line_peril_status": summarize(["line", "peril", "status"]),
        "accident_report_count_table": data.groupby(
            ["line", "loss_month", "report_month"], sort=True
        ).size().rename("claim_count").reset_index().to_dict("records"),
        "selected_associations": {
            "reporting_delay_vs_incurred_spearman": float(data["reporting_delay_days"].corr(data["incurred_to_date"], method="spearman")),
            "reporting_delay_vs_recoveries_spearman": float(data["reporting_delay_days"].corr(data["recoveries"], method="spearman")),
            "warning": "Associations are descriptive within reported claims and are selected by reporting and maturity; they do not identify causal development factors."
        },
        "largest_claims": largest.to_dict("records"),
        "limitations": [
            "Right truncation hides claims whose reporting delay exceeds observable age.",
            "Observed delay distributions are selected and are not unbiased completeness factors.",
            "Only one financial snapshot exists; historical case/paid triangles and later outcomes are unavailable.",
            "Severity, settlement and recovery associations are maturity-selected and do not identify reserve adequacy.",
        ],
    }


def _write_completeness(
    path: Path,
    policies: dict[str, pd.DataFrame],
    fits: dict[tuple[str, str], Any],
    cutoff: pd.Timestamp,
) -> tuple[int, dict[str, Any]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    row_count = 0
    summary: dict[str, Any] = {}
    try:
        for (line, peril), fit in sorted(fits.items()):
            policy = policies[line]
            completeness = average_period_completeness(
                policy["period_start"], policy["period_end"], cutoff=cutoff,
                probability=fit.probability,
            )
            output = pd.DataFrame({
                "row_id": policy["row_id"].to_numpy(),
                "line": line,
                "peril": peril,
                "count_reporting_completeness": completeness,
                "effective_reported_exposure": policy["exposure_clean"].to_numpy(dtype=float) * completeness,
                "fit_report_cutoff": cutoff.date().isoformat(),
                "estimation_scope": "full_snapshot_diagnostic_not_fold_safe",
                "occurrence_time_assumption": "uniform_daily_within_inclusive_policy_period",
            })
            table = pa.Table.from_pandas(output, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(path, table.schema, compression="zstd")
            writer.write_table(table)
            row_count += len(output)
            summary[f"{line}/{peril}"] = {
                "row_count": int(len(output)), "minimum": float(completeness.min()),
                "mean": float(completeness.mean()), "maximum": float(completeness.max()),
                "effective_reported_exposure": float(output["effective_reported_exposure"].sum()),
            }
    finally:
        if writer is not None:
            writer.close()
    return row_count, summary


def _code_provenance(root: Path, config_path: Path, scenario_path: Path) -> dict[str, Any]:
    files = [
        root / "src/iaa_hackathon/claim_targets.py", root / "src/iaa_hackathon/reporting.py",
        root / "src/iaa_hackathon/targets_pipeline.py", root / "src/iaa_hackathon/__main__.py",
        config_path, scenario_path,
    ]
    digest = hashlib.sha256()
    for path in files:
        digest.update(str(path.relative_to(root)).encode() + b"\0" + path.read_bytes() + b"\0")
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = "unavailable", True
    return {"code_config_digest": digest.hexdigest(), "files": [str(p.relative_to(root)) for p in files], "git_commit": commit, "git_dirty": dirty}


def build_targets(
    *,
    data_dir: Path,
    step2_dir: Path,
    output_dir: Path,
    target_config_path: Path,
    scenario_config_path: Path,
    project_root: Path,
) -> dict[str, Any]:
    config = json.loads(target_config_path.read_text())
    scenarios = json.loads(scenario_config_path.read_text())
    cutoff = pd.Timestamp(config["valuation_date"])
    source_before = sha256_file(data_dir / "claims.parquet")
    claims, policies, step2_manifest = _read_inputs(data_dir, step2_dir, config)

    previous_digest = None
    old_manifest = output_dir / "target-manifest.json"
    if old_manifest.is_file():
        previous_digest = json.loads(old_manifest.read_text()).get("logical_output_digest")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}-staging-", dir=output_dir.parent))
    backup: Path | None = None
    try:
        crosswalk = build_claim_crosswalk(
            claims, policies, cutoff=cutoff, source_claims_sha256=source_before, strict=True
        )
        enriched = add_observed_components(crosswalk)
        response, peril_response = build_observed_response(crosswalk, policies)
        accepted = enriched.loc[enriched["accepted_for_observed"]].copy()
        matched = enriched.loc[enriched["disposition"].eq("exactly_one_match")].copy()
        # Reporting-count diagnostics do not use the final claim status as though it
        # were known at an earlier cutoff. Status exclusions apply only to money.
        reporting_fits = fit_reporting_groups(matched, cutoff=cutoff)

        for relative in ["linkage", "targets", "diagnostics", "reporting", "scenarios"]:
            (staging / relative).mkdir(parents=True, exist_ok=True)
        crosswalk.to_parquet(staging / "linkage/claim-to-row.parquet", index=False)
        crosswalk.loc[crosswalk["disposition"].ne("exactly_one_match")].to_parquet(
            staging / "linkage/claim-exceptions.parquet", index=False
        )
        response.to_parquet(staging / "targets/observed-policy-response.parquet", index=False)
        peril_response.to_parquet(staging / "targets/observed-policy-peril-response.parquet", index=False)

        maturity = _maturity_diagnostics(matched, cutoff)
        _json_write(staging / "diagnostics/maturity.json", maturity)
        fits_json = {
            "family": "discrete geometric on nonnegative integer reporting-delay days",
            "likelihood": "log f(D) - log F(A), conditional on D <= A",
            "tail_status": "parametric extrapolation_not_observed_truth",
            "groups": [fit.to_dict() for fit in reporting_fits.values()],
        }
        _json_write(staging / "reporting/reporting-fits.json", fits_json)
        backtests = {
            "end_2022": finite_followup_backtest(matched, fit_cutoff="2022-12-31", followup_cutoff=cutoff),
            "end_2023": finite_followup_backtest(matched, fit_cutoff="2023-12-31", followup_cutoff=cutoff),
        }
        _json_write(staging / "reporting/backtests.json", backtests)
        completeness_rows, completeness_summary = _write_completeness(
            staging / "reporting/row-peril-completeness.parquet", policies, reporting_fits, cutoff
        )
        _json_write(staging / "reporting/completeness-summary.json", completeness_summary)

        scenario_impacts: list[dict[str, Any]] = []
        scenario_by_row: dict[str, pd.Series] = {}
        accepted_case = accepted.copy()
        for item in scenarios["scenarios"]:
            values = apply_reported_claim_scenario(
                accepted_case, case_multiplier=float(item["case_multiplier"]),
                future_recovery=float(item["future_recovery"]),
            )
            column = f"candidate_{item['id']}"
            accepted_case[column] = values
            by_row = accepted_case.groupby("matched_row_id", sort=False)[column].sum()
            scenario_by_row[column] = by_row
            total = float(values.sum())
            observed_total = float(accepted_case["observed_net_incurred"].sum())
            largest_bi = accepted_case.loc[accepted_case["peril"].eq("bodily_injury")].nlargest(1, "incurred_to_date")
            largest_contribution = float(values.loc[largest_bi.index].sum()) if not largest_bi.empty else 0.0
            scenario_impacts.append({
                **item, "total_candidate": total, "impact_vs_observed": total - observed_total,
                "largest_bi_claim_id": None if largest_bi.empty else str(largest_bi.iloc[0]["claim_id"]),
                "largest_bi_candidate_contribution": largest_contribution,
                "human_review_status": "pending",
            })
        _json_write(staging / "scenarios/scenario-impacts.json", {
            "formula": "paid + case_multiplier * (incurred-paid) - observed_recoveries - future_recovery",
            "trend": "disabled", "scenarios": scenario_impacts,
        })

        candidates = response[["row_id", "line", "observed_net_incurred", "accepted_reported_claim_count", "positive_observed_cost_claim_count"]].copy()
        for column, by_row in scenario_by_row.items():
            candidates[column] = candidates["row_id"].map(by_row).fillna(0.0)
        candidates["reported_claim_development_adjustment"] = candidates["candidate_reference"] - candidates["observed_net_incurred"]
        candidates["unreported_net_loss_estimate"] = np.nan
        candidates["future_recoveries_reported_claims"] = 0.0
        candidates["trend_to_2025_cost_level"] = np.nan
        candidates["target_candidate"] = candidates["candidate_reference"]
        candidates["target_version"] = "step3-reference-case-v1"
        candidates["financial_basis_status"] = "provisional"
        candidates["source_claims_sha256"] = source_before
        candidates["step2_manifest_digest"] = step2_manifest["logical_output_digest"]
        candidates["fit_population"] = pd.NA
        candidates["fit_report_cutoff"] = pd.NA
        candidates["transform_as_of_cutoff"] = cutoff.date().isoformat()
        candidates["estimation_scope"] = "scenario_only"
        assumption_ids = ["A03", "case_multiplier_reference_1", "future_recovery_0"]
        candidates["assumption_ids"] = pd.Series([assumption_ids] * len(candidates), index=candidates.index)
        candidates["human_review_status"] = "pending"
        candidates["monetary_reporting_proxy_status"] = "unavailable_count_delay_cdf_does_not_establish_amount_completeness"
        candidates.to_parquet(staging / "targets/target-candidates.parquet", index=False)

        reconciliation = monetary_reconciliation(crosswalk)
        reconciliation.update({
            "status_groups": enriched.groupby("status", sort=True).agg(
                claim_count=("claim_id", "size"), observed_net_incurred=("observed_net_incurred", "sum")
            ).reset_index().to_dict("records"),
            "accepted_by_line": accepted.groupby("line", sort=True).agg(
                claim_count=("claim_id", "size"), observed_net_incurred=("observed_net_incurred", "sum"),
                paid=("paid_to_date", "sum"), incurred=("incurred_to_date", "sum"), recoveries=("recoveries", "sum")
            ).reset_index().to_dict("records"),
            "accepted_total_observed_net_incurred_minor_units": _minor(accepted["observed_net_incurred"]),
            "policy_response_total_minor_units": _minor(response["observed_net_incurred"]),
            "policy_row_count": int(len(response)),
            "zero_claim_policy_row_count": int(response["accepted_reported_claim_count"].eq(0).sum()),
            "peril_response_total_minor_units": _minor(peril_response["observed_net_incurred"]),
            "completeness_row_count": completeness_rows,
            "identity_checks": {
                "one_crosswalk_row_per_source_claim": len(crosswalk) == len(claims) and crosswalk["claim_id"].is_unique,
                "accepted_claims_equal_policy_counts": int(accepted.shape[0]) == int(response["accepted_reported_claim_count"].sum()),
                "observed_money_conserved": _minor(accepted["observed_net_incurred"]) == _minor(response["observed_net_incurred"]) == _minor(peril_response["observed_net_incurred"]),
                "all_policy_rows_preserved": len(response) == sum(len(frame) for frame in policies.values()),
                "reference_scenario_identity": bool(np.allclose(candidates["candidate_reference"], candidates["observed_net_incurred"], atol=1e-8)),
            },
        })
        if not all(reconciliation["identity_checks"].values()):
            raise ClaimTargetError(f"Step 3 reconciliation failed: {reconciliation['identity_checks']}")
        _json_write(staging / "target-reconciliation.json", reconciliation)

        output_files = sorted(p for p in staging.rglob("*") if p.is_file())
        hashes = {str(p.relative_to(staging)): sha256_file(p) for p in output_files}
        logical = hashlib.sha256()
        for name, digest in hashes.items():
            logical.update(name.encode() + b"\0" + digest.encode() + b"\0")
        source_after = sha256_file(data_dir / "claims.parquet")
        manifest = {
            "schema_version": 1, "status": "complete",
            "scope": "Step 3 claim linkage, observed response, delay diagnostics, and conditional scenarios; no pricing model, split, test target, or prediction.",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "logical_output_digest": logical.hexdigest(), "outputs": hashes,
            "source_claims_sha256_before": source_before, "source_claims_sha256_after": source_after,
            "raw_hashes_unchanged": source_before == source_after,
            "step2_manifest_digest": step2_manifest["logical_output_digest"],
            "target_config_id": config["config_id"], "scenario_config_id": scenarios["config_id"],
            "provenance": _code_provenance(project_root, target_config_path, scenario_config_path),
            "runtime": {"python": platform.python_version(), "pandas": pd.__version__, "pyarrow": pa.__version__, "scipy": scipy.__version__},
            "rerun_comparison": {"previous_logical_output_digest": previous_digest, "matches_previous_run": previous_digest == logical.hexdigest() if previous_digest else None},
        }
        _json_write(staging / "target-manifest.json", manifest)

        if output_dir.exists():
            backup = output_dir.with_name(f".{output_dir.name}-previous-{os.getpid()}")
            output_dir.replace(backup)
        staging.replace(output_dir)
        if backup is not None:
            shutil.rmtree(backup)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        if backup is not None and backup.exists() and not output_dir.exists():
            backup.replace(output_dir)
        raise
