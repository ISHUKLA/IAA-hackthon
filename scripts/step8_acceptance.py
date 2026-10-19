"""Independent actual-data acceptance of the registered S8 experiment."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import subprocess

import joblib
import numpy as np
import pandas as pd
import pyarrow.dataset as ds

from iaa_hackathon.baselines import BASE_FEATURES, score_vector
from iaa_hackathon.complexity_preflight import align_predictions
from iaa_hackathon.lightgbm_challenger import sha256
from iaa_hackathon.restricted_complexity import FEATURE, promotion_decision
from iaa_hackathon.validation_scoring import score_supplied_predictions


root = Path("outputs/step8")
cfg_path = Path("configs/step8_complexity_gate.json")
cfg = json.loads(cfg_path.read_text())
out = Path(cfg["computational_budget"]["output_dir"])
manifest = json.loads((out / "manifest.json").read_text())
decision = json.loads((root / "decision.json").read_text())
frozen = json.loads((root / "benchmark-frozen.json").read_text())
if manifest["status"] != "complete" or manifest["candidate_fits"] != 2:
    raise ValueError("Step 8 run is incomplete")
if decision["decision"] != promotion_decision(decision["promotion_gates"]):
    raise ValueError("decision does not follow all seven promotion gates")
if sha256(cfg_path) != manifest["inputs"]["config_sha256"] or sha256(root / "decision.json") != manifest["decision_sha256"]:
    raise ValueError("decision or predeclared rule changed")
if sha256(root / "benchmark-frozen.json") != cfg["benchmark_frozen_sha256"] or sha256(root / "diagnosis.json") != cfg["diagnosis_sha256"]:
    raise ValueError("registered benchmark or diagnosis changed")
for path, expected in frozen["artifacts_sha256"].items():
    if sha256(Path(path)) != expected:
        raise ValueError(f"upstream benchmark artifact changed: {path}")
for path, expected in manifest["inputs"]["code_sha256"].items():
    if sha256(Path(path)) != expected:
        raise ValueError(f"experiment code changed: {path}")
for path, expected in manifest["artifacts_sha256"].items():
    if sha256(out / path) != expected:
        raise ValueError(f"experiment artifact changed: {path}")
events = {event["event"]: event["at_ns"] for event in manifest["events"]}
if not events["gate_registered"] < events["candidate_fit_started"] < events["primary_specification_frozen"] < events["challenge_rows_first_loaded_for_candidate"] < events["challenge_evaluated_once"]:
    raise ValueError("gate, selection or challenge chronology failed")
if sha256(out / "selection-frozen.json") != manifest["selection_frozen_sha256"]:
    raise ValueError("primary selection changed")
columns = sorted(set(["row_id", "period_start", "line", "exposure_clean", "observed_net_incurred", *BASE_FEATURES["contents"], "works_from_home", "lodgers", "bicycle_cover", "high_value_items"]))
dataset = ds.dataset("outputs/step2/repairs/model/training-model-table.parquet")
data = dataset.to_table(columns=columns).to_pandas()
years = pd.to_datetime(data.period_start).dt.year
counts = {}
scores = {}
benchmark_tail_review = {}
for fold, year, training_years in (("F2023", 2023, [2021, 2022]), ("F2024", 2024, [2021, 2022, 2023])):
    valid = data[years.eq(year)]
    metadata = pd.read_parquet(out / "predictions" / f"{fold}-candidate.parquet")
    prediction = align_predictions(valid, metadata, fold=fold, response=cfg["response_version"])
    if not metadata.run_id.eq(manifest["run_fingerprint"]).all() or not metadata.config_sha256.eq(manifest["inputs"]["config_sha256"]).all():
        raise ValueError("prediction metadata provenance differs from experiment")
    baseline = align_predictions(valid, pd.read_parquet(f"outputs/step6/features/predictions/{fold}-selected.parquet"), fold=fold, response=cfg["response_version"])
    benchmark_tail_review[fold] = []
    for quantile in (.99, .999):
        tail = baseline >= np.quantile(baseline, quantile)
        actual = valid.loc[tail, "observed_net_incurred"].to_numpy(float)
        benchmark_tail_review[fold].append({"tail_definition": "benchmark prediction rank", "quantile": quantile, "rows": int(tail.sum()), "benchmark": score_vector(actual, baseline[tail]), "candidate": score_vector(actual, prediction[tail])})
    mask = valid.line.eq("contents").to_numpy()
    if not np.array_equal(prediction[~mask], baseline[~mask]):
        raise ValueError("motor or buildings predictions changed")
    model = joblib.load(out / "models" / f"{fold}-contents.joblib")
    training = data[years.isin(training_years) & data.line.eq("contents")]
    expected_knots = np.quantile(np.log1p(training.sum_insured_repaired.dropna()), [.2, .5, .8])
    if not np.allclose(model.knots, expected_knots, rtol=0, atol=1e-12):
        raise ValueError("candidate knots are not training-only")
    if model.source_features != cfg["benchmark_features"]["contents"] or model.blocks != cfg["benchmark_blocks"]["contents"]:
        raise ValueError("candidate changed the base feature specification")
    if model.alpha != cfg["glm"]["alpha"] or model.max_iter != cfg["glm"]["max_iter"]:
        raise ValueError("candidate changed baseline model settings")
    if model.matrix(valid.loc[mask]).columns.tolist() != [*cfg["benchmark_features"]["contents"], FEATURE]:
        raise ValueError("candidate feature allowlist changed")
    if not np.allclose(model.predict(valid.loc[mask]), prediction[mask], rtol=1e-12, atol=1e-10):
        raise ValueError("saved model reload predictions differ")
    scorer = score_supplied_predictions(valid[["row_id", "observed_net_incurred"]].rename(columns={"observed_net_incurred": "observed_net_baseline"}), metadata, fold_id=fold, response_version=cfg["response_version"])
    recorded = decision["folds"][fold]["candidate"]
    if not np.isclose(scorer["mean_tweedie_deviance"], recorded["mean_tweedie_deviance"], rtol=1e-12, atol=1e-12):
        raise ValueError("candidate score does not reproduce under existing Step 4 scorer")
    counts[fold] = len(valid)
    scores[fold] = scorer
ignored = subprocess.run(["git", "check-ignore", str(out / "models/F2023-contents.joblib"), str(out / "predictions/F2023-candidate.parquet")], check=True, text=True, capture_output=True)
if len(ignored.stdout.splitlines()) != 2:
    raise ValueError("model/prediction Git exclusions failed")
report = {"status": "passed", "decision": decision["decision"], "rows": counts, "seven_gates_recorded": True, "registered_before_fitting": True, "single_frozen_challenge": True, "train_only_knots": True, "base_features_and_settings_unchanged": True, "other_lines_bitwise_unchanged": True, "models_reload_equivalently": True, "upstream_hashes_unchanged": True, "power": 1.5, "prediction_unit": "policy_period_cost", "scores_reproduced": scores}
(root / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
(root / "benchmark-tail-review.json").write_text(json.dumps({"status": "complete", "purpose": "post-fit acceptance diagnostic only; no selection or fitting uses these values", "folds": benchmark_tail_review}, indent=2) + "\n")
print(json.dumps(report, indent=2))
