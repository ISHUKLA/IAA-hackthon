"""Reconcile the repaired Step 2 observed baseline and reporting delays.

This is descriptive only: it does not construct an ultimate target or apply
IBNR, development, recovery, or trend adjustments.
"""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def input_paths(step2_dir: Path) -> dict[str, Path]:
    """Locate the Step 2 repair build's deliberately nested output layout."""
    paths = {
        "training_model_table.parquet": step2_dir / "model" / "training-model-table.parquet",
        "claims_matched.parquet": step2_dir / "claims" / "matched.parquet",
        "claims_quarantined.parquet": step2_dir / "claims" / "quarantined.parquet",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing Step 2 repair inputs: " + ", ".join(missing))
    return paths


def require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step2-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.step2_dir, args.output_dir
    if source.resolve() == out.resolve():
        raise ValueError("Output directory must differ from Step 2 directory")

    paths = input_paths(source)
    policies = pd.read_parquet(paths["training_model_table.parquet"])[
        ["row_id", "line", "period_start", "exposure", "exposure_raw", "exposure_clean", "observed_net_incurred"]
    ].copy()
    policies["policy_year"] = pd.to_datetime(policies["period_start"]).dt.year
    policies = policies.drop(columns="period_start")
    if policies["exposure_clean"].isna().any() or (policies["exposure_clean"] <= 0).any():
        raise ValueError("Corrected exposure must be positive and non-null")
    # The repair build preserves raw source exposure in `exposure`; use the
    # separately named ACT/365 result for a corrected-exposure diagnostic.
    policies["exposure"] = policies["exposure_clean"]
    policies = policies.drop(columns=["exposure_raw", "exposure_clean"])
    matched = pd.read_parquet(paths["claims_matched.parquet"])
    quarantine = pd.read_parquet(paths["claims_quarantined.parquet"])
    require_columns(
        matched,
        {
            "claim_id", "matched_row_id", "line", "peril", "loss_date", "report_date",
            "status", "incurred_to_date", "recoveries", "accepted_for_observed",
        },
        "matched claims",
    )
    require_columns(quarantine, {"line", "status", "incurred_to_date", "recoveries"}, "quarantined claims")

    if policies["row_id"].isna().any() or policies["row_id"].duplicated().any():
        raise ValueError("Policy row_id is not unique and non-null")
    if policies["exposure"].isna().any() or (policies["exposure"] <= 0).any():
        raise ValueError("Exposure must be positive and non-null")

    claims = matched.loc[
        matched["accepted_for_observed"].astype(bool)
        & matched["status"].astype("string").str.lower().isin(["open", "closed"])
    ].copy()
    if claims["claim_id"].isna().any() or claims["claim_id"].duplicated().any():
        raise ValueError("Matched accepted claim_id is not unique and non-null")
    required = ["matched_row_id", "loss_date", "report_date", "incurred_to_date", "recoveries"]
    if claims[required].isna().any().any():
        raise ValueError("Matched accepted claims contain missing required values")
    claims["loss_date"] = pd.to_datetime(claims["loss_date"])
    claims["report_date"] = pd.to_datetime(claims["report_date"])
    if (claims["report_date"] < claims["loss_date"]).any():
        raise ValueError("Report date precedes loss date")

    claims["claim_net"] = claims["incurred_to_date"] - claims["recoveries"]
    claims["accident_year"] = claims["loss_date"].dt.year
    by_policy = claims.groupby("matched_row_id", as_index=False)["claim_net"].sum()
    by_policy = by_policy.rename(columns={"matched_row_id": "row_id", "claim_net": "recomputed_net"})
    joined = policies.merge(by_policy, how="left", on="row_id", validate="one_to_one")
    joined["recomputed_net"] = joined["recomputed_net"].fillna(0.0)
    unmatched_ids = int((~by_policy["row_id"].isin(policies["row_id"])).sum())
    difference = float((joined["observed_net_incurred"] - joined["recomputed_net"]).abs().max())
    if unmatched_ids or difference > 0.01:
        raise ValueError(f"Policy reconciliation failed: unmatched={unmatched_ids}, max difference={difference}")

    out.mkdir(parents=True, exist_ok=True)
    baseline = policies.rename(columns={"observed_net_incurred": "observed_net_baseline"})
    baseline.to_parquet(out / "policy_observed_baseline.parquet", index=False)
    by_line_year = baseline.groupby(["line", "policy_year"], as_index=False).agg(
        policy_rows=("row_id", "size"), exposure=("exposure", "sum"), observed_net=("observed_net_baseline", "sum")
    )
    by_line_year["observed_net_per_exposure"] = by_line_year["observed_net"] / by_line_year["exposure"]
    by_line_year.sort_values(["line", "policy_year"]).to_csv(out / "baseline_by_line_year.csv", index=False)

    claims["reported_by_year_end"] = claims["report_date"] <= pd.to_datetime(
        claims["accident_year"].astype(str) + "-12-31"
    )
    reporting = claims.groupby(["line", "peril", "accident_year"], as_index=False).agg(
        known_claims=("claim_id", "size"),
        reported_by_year_end=("reported_by_year_end", "sum"),
        known_current_net=("claim_net", "sum"),
        early_reported_current_net=("claim_net", lambda values: values.loc[claims.loc[values.index, "reported_by_year_end"]].sum()),
        open_claims=("status", lambda values: values.astype("string").str.lower().eq("open").sum()),
    )
    reporting["known_count_fraction_reported_by_year_end"] = reporting["reported_by_year_end"] / reporting["known_claims"]
    reporting["known_amount_fraction_reported_by_year_end"] = reporting["early_reported_current_net"] / reporting["known_current_net"].replace(0, float("nan"))
    reporting.sort_values(["line", "peril", "accident_year"]).to_csv(out / "reporting_diagnostics.csv", index=False)

    quarantine_summary = quarantine.assign(
        net_incurred=quarantine["incurred_to_date"] - quarantine["recoveries"]
    ).groupby(["line", "status"], as_index=False).agg(
        claims=("status", "size"), net_incurred=("net_incurred", "sum")
    )
    quarantine_summary.sort_values(["line", "status"]).to_csv(out / "quarantined_summary.csv", index=False)

    metadata = {
        "status": "diagnostic baseline; competition target and actual valuation date not verified",
        "accepted_matched_claims": int(len(claims)),
        "policy_rows": int(len(policies)),
        "quarantined_claim_rows_all_statuses": int(len(quarantine)),
        "observed_net_incurred": float(baseline["observed_net_baseline"].sum()),
        "maximum_policy_reconciliation_difference": difference,
        "exposure_basis": "Step 2 exposure_clean (inclusive ACT/365); the model-table exposure column preserves source exposure_raw",
        "latest_observed_report_date_proxy_only": str(claims["report_date"].max().date()),
        "limitations": [
            "Observed net incurred is not verified as the competition target or ultimate loss.",
            "Reporting fractions only describe claims known in the supplied snapshot; remaining unreported claims are invisible.",
            "Historical reporting fractions use current financial values and cannot reconstruct past reserve development.",
            "No IBNR, reserve development, future recoveries, or inflation/trend adjustments have been applied.",
            "Current snapshot labels can leak future information into temporal validation; construct fold-specific labels when possible.",
            "Quarantined claims are excluded from the baseline and require investigation.",
        ],
        "input_sha256": {name: digest(path) for name, path in paths.items()},
    }
    (out / "step3_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
