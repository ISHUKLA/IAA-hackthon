"""Diagnose only the primary benchmark and derive a gate before fitting."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import time
import sys

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
from sklearn.metrics import mean_tweedie_deviance

from iaa_hackathon.complexity_preflight import align_predictions
from iaa_hackathon.lightgbm_challenger import paired_uncertainty, report_pair, sha256


out = Path("outputs/step8")
preflight = json.loads((out / "preflight.json").read_text())
if preflight["preflight_status"] != "ready":
    raise ValueError("Step 8 preflight has not passed")
diagnosis_path = out / "diagnosis.json"
diagnosis_code = sha256(Path(__file__))
if diagnosis_path.exists():
    existing = json.loads(diagnosis_path.read_text())
    if existing.get("benchmark_frozen_sha256") == sha256(out / "benchmark-frozen.json") and existing.get("diagnosis_code_sha256") == diagnosis_code:
        print(json.dumps({"status": "reused_verified_diagnosis", "materiality": existing["materiality"]}))
        sys.exit(0)
started = time.perf_counter()
columns = ["row_id", "customer_id_clean", "customer_id", "policy_id", "period_start", "line", "exposure_clean", "observed_net_incurred", "driver_age", "sum_insured_repaired", "occupancy", "cover_type", "security_level", "new_business"]
data = ds.dataset("outputs/step2/repairs/model/training-model-table.parquet").to_table(columns=columns, filter=ds.field("period_start") < datetime(2024, 1, 1)).to_pandas()
year = pd.to_datetime(data.period_start).dt.year
train = data[year.isin([2021, 2022])]
valid = data[year.eq(2023)].copy()
version = preflight["existing_evidence_reverified"]["S7_decision"]["response_version"]
glm = align_predictions(valid, pd.read_parquet("outputs/step6/features/predictions/F2023-selected.parquet"), fold="F2023", response=version)
lgb = align_predictions(valid, pd.read_parquet("outputs/step7/predictions/F2023-selected.parquet"), fold="F2023", response=version)
valid["returning_customer"] = valid.customer_id_clean.isin(set(train.customer_id_clean))
valid["returning_policy"] = valid.policy_id.isin(set(train.policy_id))
primary = report_pair(valid, glm, lgb)
dimensions = []
for line, field in (("motor", "driver_age"), ("buildings", "sum_insured_repaired"), ("contents", "sum_insured_repaired")):
    mask = valid.line.eq(line).to_numpy()
    training = train[train.line.eq(line)]
    values = training[field].dropna().to_numpy(float)
    edges = np.unique(np.quantile(values, [0, .2, .4, .6, .8, 1]))
    edges[0], edges[-1] = -np.inf, np.inf
    bands = pd.cut(valid.loc[mask, field], edges, labels=False)
    for band in sorted(bands.dropna().unique()):
        local = bands.eq(band).to_numpy()
        subset = valid.loc[mask].loc[local]
        prediction = glm[mask][local]
        ratio = float(subset.observed_net_incurred.sum() / prediction.sum())
        clusters = pd.DataFrame({"customer": subset.customer_id_clean.to_numpy(), "y": subset.observed_net_incurred.to_numpy(float), "mu": prediction}).groupby("customer", sort=True).agg(y=("y", "sum"), mu=("mu", "sum"))
        rng = np.random.default_rng(20261019)
        ratios = []
        for _ in range(200):
            selected = rng.integers(0, len(clusters), len(clusters))
            ratios.append(float(clusters.y.to_numpy()[selected].sum() / clusters.mu.to_numpy()[selected].sum()))
        dimensions.append({"line": line, "field": field, "training_quantile_band": int(band) + 1, "rows": len(subset), "A_over_E": ratio, "AE_ci95_customer_bootstrap": np.quantile(ratios, [.025, .975]).tolist(), "reference_sum": float(subset.observed_net_incurred.sum()), "prediction_sum": float(prediction.sum()), "training_edges": [None if not np.isfinite(x) else float(x) for x in edges]})
contents_mask = valid.line.eq("contents").to_numpy()
reference_uncertainty = paired_uncertainty(valid.loc[contents_mask], glm[contents_mask], lgb[contents_mask], seed=20261019, repeats=200)
share = float(contents_mask.mean())
lower, upper = reference_uncertainty["mean_deviance_gain_ci95"]
null_deviance = float(mean_tweedie_deviance(valid.observed_net_incurred, np.full(len(valid), valid.observed_net_incurred.mean()), power=1.5))
threshold = max((upper - lower) * .5 * share, float(np.spacing(primary["overall"]["glm"]["mean_tweedie_deviance"]) * 100))
payload = {"status": "complete", "diagnosis_code_sha256": diagnosis_code, "primary_fold": "F2023", "benchmark": "S6_selected_compact_tweedie_glm", "response_version": version, "benchmark_frozen_sha256": sha256(out / "benchmark-frozen.json"), "primary_diagnostics": primary, "risk_dimensions": dimensions, "reference_contents_uncertainty": reference_uncertainty, "materiality": {"rule": "half the prior S6-vs-S7 contents paired 95% interval width, converted to pooled-row scale; also require the new candidate paired interval lower bound > 0", "minimum_pooled_mean_deviance_gain": threshold, "equivalent_minimum_D2_gain": threshold / null_deviance, "contents_row_share": share, "reference_ci95": [lower, upper], "declared_before_candidate_fit": True, "universal_threshold": False}, "candidate_hypothesis": "a single train-quantile contents insured-value curvature term may address intermediate insured-value residual underprediction", "training_log_insured_tent_knots": np.quantile(np.log1p(train.loc[train.line.eq("contents"), "sum_insured_repaired"].dropna().to_numpy(float)), [.2, .5, .8]).tolist(), "runtime_seconds": time.perf_counter() - started, "completed_at_ns": time.time_ns()}
(out / "diagnosis.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
print(json.dumps({"status": "complete", "primary_contents_risk_dimensions": [item for item in dimensions if item["line"] == "contents"], "materiality": payload["materiality"], "runtime_seconds": payload["runtime_seconds"]}, indent=2))
