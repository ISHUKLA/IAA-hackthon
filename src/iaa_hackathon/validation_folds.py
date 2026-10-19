"""Deterministic calendar-fold membership for Step 4; no model fitting."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


class FoldError(ValueError):
    pass


def build_membership(policies: pd.DataFrame, config: dict) -> pd.DataFrame:
    required = {"row_id", "policy_id", "customer_id", "line", "period_start", "period_end", "exposure_clean"}
    missing = required - set(policies.columns)
    if missing:
        raise FoldError(f"missing policy fields: {sorted(missing)}")
    frame = policies.copy()
    frame["period_start"] = pd.to_datetime(frame["period_start"], errors="coerce")
    frame["period_end"] = pd.to_datetime(frame["period_end"], errors="coerce")
    if frame["row_id"].isna().any() or frame["row_id"].duplicated().any():
        raise FoldError("row_id must be unique and non-null")
    if frame[["period_start", "period_end"]].isna().any().any() or (frame.period_end < frame.period_start).any():
        raise FoldError("policy periods must be valid")
    frame["period_year"] = frame.period_start.dt.year
    if (frame.period_end.dt.year != frame.period_year).any():
        raise FoldError("cross-year policy periods are not permitted in calendar folds")
    pieces = []
    for fold in config["folds"]:
        train = frame.period_year.isin(fold["train_years"])
        valid = frame.period_year.eq(fold["validation_year"])
        if (train & valid).any():
            raise FoldError(f"overlapping roles in {fold['id']}")
        selected = frame.loc[train | valid, ["row_id", "policy_id", "customer_id", "line", "period_year", "exposure_clean"]].copy()
        selected["fold_id"] = fold["id"]
        selected["role"] = "train"
        selected.loc[valid.loc[selected.index], "role"] = "validation"
        selected["input_identity"] = config["input_universe"]["policy_bundle"]
        pieces.append(selected)
    result = pd.concat(pieces, ignore_index=True)
    if result.duplicated(["fold_id", "row_id"]).any():
        raise FoldError("a row has more than one role in a fold")
    return result.sort_values(["fold_id", "role", "row_id"], kind="stable").reset_index(drop=True)


def membership_digest(membership: pd.DataFrame) -> str:
    columns = ["fold_id", "row_id", "role", "period_year", "input_identity"]
    payload = membership[columns].sort_values(columns, kind="stable").to_csv(index=False).encode()
    return hashlib.sha256(payload).hexdigest()


def fold_summary(membership: pd.DataFrame, responses: pd.DataFrame) -> dict:
    response = responses[["row_id", "observed_net_baseline"]]
    joined = membership.merge(response, on="row_id", how="left", validate="many_to_one")
    if joined.observed_net_baseline.isna().any():
        raise FoldError("response view does not cover fold membership")
    grouped = joined.groupby(["fold_id", "role", "line", "period_year"], as_index=False).agg(
        rows=("row_id", "size"), exposure=("exposure_clean", "sum"), observed_net=("observed_net_baseline", "sum")
    )
    return {"membership_digest": membership_digest(membership), "by_fold_role_line_year": grouped.to_dict("records")}


def write_fold_build(policy_path: Path, response_path: Path, config_path: Path, output_dir: Path) -> dict:
    config = json.loads(config_path.read_text())
    membership = build_membership(pd.read_parquet(policy_path), config)
    summary = fold_summary(membership, pd.read_parquet(response_path))
    output_dir.mkdir(parents=True, exist_ok=True)
    membership.to_parquet(output_dir / "fold-membership.parquet", index=False)
    (output_dir / "fold-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary
