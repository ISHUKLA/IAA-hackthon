"""Verify actual S7 artifacts, identical scored IDs, provenance and reloads."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import lightgbm as lgb
import numpy as np
import pandas as pd

from iaa_hackathon.baselines import BASE_FEATURES
from iaa_hackathon.complexity_preflight import align_predictions
from iaa_hackathon.lightgbm_challenger import FeaturePipeline, period_prediction, sha256
from iaa_hackathon.metrics import metric_report
from iaa_hackathon.validation_scoring import score_supplied_predictions


def main() -> int:
    out = Path("outputs/step7")
    manifest = json.loads((out / "manifest.json").read_text())
    cfg = json.loads(Path("configs/step7_lightgbm.json").read_text())
    s6_results = json.loads(Path("outputs/step6/features/results.json").read_text())
    s6_manifest = json.loads(Path("outputs/step6/features/manifest.json").read_text())
    s6_features = {row["line"]: row["features"] for row in s6_results if row.get("fold_id") == "F2023" and row.get("candidate") == "selected_combined" and row["line"] != "pooled"}
    if cfg["features"] != s6_features or cfg["blocks"] != s6_manifest["selected_blocks"]:
        raise ValueError("Phase A feature specification differs from accepted S6 benchmark")
    if manifest["status"] != "complete" or manifest["challenge_evaluations"] != 1:
        raise ValueError("actual S7 run is incomplete")
    if sha256(Path("configs/step7_lightgbm.json")) != manifest["config"]:
        raise ValueError("configuration changed after training")
    for name, expected in manifest["artifacts_sha256"].items():
        if sha256(out / name) != expected:
            raise ValueError(f"run artifact changed: {name}")
    for name, expected in manifest["code"].items():
        if sha256(Path(name)) != expected:
            raise ValueError(f"model code changed: {name}")
    paths = {"policy": Path("outputs/step2/repairs/model/training-model-table.parquet"), "claims": Path("outputs/step2/repairs/claims/matched.parquet"), "fold_membership": Path("outputs/step4/folds/fold-membership.parquet"), "S6_manifest": Path("outputs/step6/features/manifest.json")}
    for name, path in paths.items():
        if sha256(path) != manifest["inputs"][name]:
            raise ValueError(f"upstream input changed: {path}")
    events = {item["event"]: item["at_ns"] for item in manifest["events"]}
    if not events["selection_frozen"] < events["challenge_rows_first_loaded_for_lightgbm"] < events["challenge_evaluated_once"]:
        raise ValueError("challenge was accessed before primary selection was frozen")
    freeze_path = out / "selection-frozen.json"
    if sha256(freeze_path) != manifest["selection_frozen_sha256"]:
        raise ValueError("frozen selection changed")
    frozen = json.loads(freeze_path.read_text())
    blocks_config = json.loads(Path("configs/features.json").read_text())
    source = set(sum(BASE_FEATURES.values(), []))
    for line, blocks in cfg["blocks"].items():
        for block in blocks:
            source.update(blocks_config["blocks"][line][block]["source"])
    frame = pd.read_parquet(paths["policy"], columns=["row_id", "period_start", "line", "exposure_clean", "observed_net_incurred", *sorted(source)])
    frame["period_year"] = pd.to_datetime(frame.period_start).dt.year
    member = pd.read_parquet(paths["fold_membership"], columns=["row_id", "fold_id", "role"])
    counts = {}
    diagnostics = {}
    for fold_id, year in (("F2023", 2023), ("F2024", 2024)):
        valid = frame[frame.period_year.eq(year)]
        supplied = pd.read_parquet(out / "predictions" / f"{fold_id}-selected.parquet")
        for column, value in (("run_id", manifest["run_fingerprint"]), ("config_sha256", manifest["config"]), ("input_policy_sha256", manifest["inputs"]["policy"])):
            if not supplied[column].eq(value).all():
                raise ValueError(f"prediction provenance mismatch: {column}")
        prediction = align_predictions(valid, supplied, fold=fold_id, response=cfg["response_version"])
        reference_member = member[member.fold_id.eq(fold_id) & member.role.eq("validation")]
        if set(reference_member.row_id) != set(valid.row_id) or len(reference_member) != len(valid):
            raise ValueError("scored rows differ from frozen fold membership")
        baseline_path = Path(f"outputs/step6/features/predictions/{fold_id}-selected.parquet")
        if sha256(baseline_path) != cfg["benchmark_prediction_sha256"][fold_id]:
            raise ValueError("Step 6 comparison predictions changed")
        align_predictions(valid, pd.read_parquet(baseline_path), fold=fold_id, response=cfg["response_version"])
        reloaded = np.empty(len(valid))
        for line in cfg["features"]:
            mask = valid.line.eq(line).to_numpy()
            pipeline = FeaturePipeline(**json.loads((out / "models" / f"{fold_id}-{line}-selected-pipeline.json").read_text()))
            model = lgb.Booster(model_file=str(out / "models" / f"{fold_id}-{line}-selected.txt"))
            if model.feature_name() != cfg["features"][line] or pipeline.allowed != cfg["features"][line]:
                raise ValueError("actual model matrix differs from Phase A feature allowlist")
            if fold_id == "F2024" and model.current_iteration() != frozen["selection"][line]["rounds"]:
                raise ValueError("challenge refit used non-frozen boosting rounds")
            reloaded[mask] = period_prediction(model, pipeline, valid.loc[mask])
        if not np.allclose(reloaded, prediction, rtol=1e-12, atol=1e-10):
            raise ValueError("actual selected saved-model predictions do not reload equivalently")
        diagnostic = json.loads((out / f"{fold_id}-diagnostics.json").read_text())
        measured = metric_report(valid.observed_net_incurred.to_numpy(float), prediction)
        scorer_result = score_supplied_predictions(valid[["row_id", "observed_net_incurred"]].rename(columns={"observed_net_incurred": "observed_net_baseline"}), supplied, fold_id=fold_id, response_version=cfg["response_version"])
        if not np.isclose(measured["mean_tweedie_deviance"], scorer_result["mean_tweedie_deviance"], rtol=1e-12, atol=1e-12):
            raise ValueError("period scoring differs from existing Step 4 supplied-prediction scorer")
        if not np.isclose(measured["mean_tweedie_deviance"], diagnostic["overall"]["lightgbm"]["mean_tweedie_deviance"], rtol=1e-12, atol=1e-12):
            raise ValueError("recorded actual score cannot be reproduced")
        diagnostics[fold_id] = measured
        counts[fold_id] = len(valid)
    ignored = subprocess.run(["git", "check-ignore", str(out / "predictions/F2023-selected.parquet"), str(out / "models/F2023-motor-selected.txt")], capture_output=True, text=True, check=True)
    if len(ignored.stdout.splitlines()) != 2:
        raise ValueError("row predictions or models are not excluded from Git")
    result = {"status": "passed", "rows": counts, "all_three_lines": True, "reload_equivalent": True, "Phase_A_features_equal_S6": True, "upstream_hashes_unchanged": True, "challenge_after_selection_frozen": True, "challenge_evaluations": 1, "power": 1.5, "prediction_unit": "policy_period_cost", "scores_reproduced": diagnostics}
    # Acceptance is deliberately external to the immutable training manifest.
    (out / "acceptance.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
