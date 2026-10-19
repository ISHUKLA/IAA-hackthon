"""Persist aggregate S5/S6 segment and large-claim sensitivity diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from iaa_hackathon.baselines import score_vector


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scored_group(frame: pd.DataFrame, prediction_column: str) -> dict:
    return score_vector(
        frame["observed_net_incurred"].to_numpy(float),
        frame[prediction_column].to_numpy(float),
    )


parser = argparse.ArgumentParser()
parser.add_argument("--step2-dir", type=Path, required=True)
parser.add_argument("--baseline-dir", type=Path, required=True)
parser.add_argument("--feature-dir", type=Path, required=True)
args = parser.parse_args()

model_path = args.step2_dir / "model/training-model-table.parquet"
claims_path = args.step2_dir / "claims/matched.parquet"
columns = [
    "row_id", "policy_id", "customer_id", "period_start", "line",
    "new_business", "observed_net_incurred",
]
data = pd.read_parquet(model_path, columns=columns)
data["period_year"] = pd.to_datetime(data["period_start"]).dt.year
claims = pd.read_parquet(
    claims_path,
    columns=["claim_id", "matched_row_id", "line", "peril", "loss_date", "observed_net_incurred"],
)

report: dict = {
    "status": "complete",
    "inputs": {
        "training_model_table_sha256": sha256(model_path),
        "matched_claims_sha256": sha256(claims_path),
    },
    "definitions": {
        "returning_policy": "policy_id appears in an earlier training year",
        "returning_customer": "customer_id appears in an earlier training year",
        "new_business": "supplied policy-period field; reported as a segment, not used to redefine return status",
        "tail_sensitivity": "subtract the largest linked claim amount from its held-out row response; keep every row and prediction fixed",
    },
    "folds": {},
}

for fold_id, valid_year in (("F2023", 2023), ("F2024", 2024)):
    training = data[data["period_year"] < valid_year]
    valid = data[data["period_year"] == valid_year].copy()
    valid["returning_policy"] = valid["policy_id"].isin(set(training["policy_id"]))
    valid["returning_customer"] = valid["customer_id"].isin(set(training["customer_id"]))

    baseline = pd.read_parquet(
        args.baseline_dir / "predictions" / f"{fold_id}-B3_compact_tweedie_glm.parquet",
        columns=["row_id", "prediction"],
    ).rename(columns={"prediction": "s5_prediction"})
    feature = pd.read_parquet(
        args.feature_dir / "predictions" / f"{fold_id}-selected.parquet",
        columns=["row_id", "prediction"],
    ).rename(columns={"prediction": "s6_prediction"})
    joined = valid.merge(baseline, on="row_id", how="left", validate="one_to_one").merge(
        feature, on="row_id", how="left", validate="one_to_one"
    )
    if joined[["s5_prediction", "s6_prediction"]].isna().any().any():
        raise ValueError(f"{fold_id}: incomplete prediction coverage")

    segments = []
    for field in ("line", "returning_policy", "returning_customer", "new_business"):
        for value, group in joined.groupby(field, dropna=False, observed=True):
            label = None if pd.isna(value) else value.item() if isinstance(value, np.generic) else value
            segments.append({
                "field": field,
                "value": label,
                "rows": int(len(group)),
                "s5": scored_group(group, "s5_prediction"),
                "s6": scored_group(group, "s6_prediction"),
            })

    fold_claims = claims[pd.to_datetime(claims["loss_date"]).dt.year == valid_year]
    largest = fold_claims.loc[fold_claims["observed_net_incurred"].idxmax()]
    tail = joined.copy()
    match = tail["row_id"].eq(largest["matched_row_id"])
    if int(match.sum()) != 1:
        raise ValueError(f"{fold_id}: largest claim does not map to one held-out row")
    adjusted = float(tail.loc[match, "observed_net_incurred"].iloc[0]) - float(largest["observed_net_incurred"])
    if adjusted < -1e-8:
        raise ValueError(f"{fold_id}: claim amount exceeds linked row response")
    tail.loc[match, "observed_net_incurred"] = max(adjusted, 0.0)
    report["folds"][fold_id] = {
        "rows": int(len(joined)),
        "segments": segments,
        "tail_sensitivity": {
            "claim_id": largest["claim_id"],
            "row_id": largest["matched_row_id"],
            "line": largest["line"],
            "peril": largest["peril"],
            "claim_amount": float(largest["observed_net_incurred"]),
            "s5_primary": scored_group(joined, "s5_prediction"),
            "s5_adjusted": scored_group(tail, "s5_prediction"),
            "s6_primary": scored_group(joined, "s6_prediction"),
            "s6_adjusted": scored_group(tail, "s6_prediction"),
        },
    }

output = args.feature_dir / "diagnostics.json"
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"status": report["status"], "output": str(output), "folds": list(report["folds"])}, indent=2))
