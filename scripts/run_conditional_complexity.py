"""One preregistered S8 contents refinement with all seven promotion gates."""
from __future__ import annotations

from datetime import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import resource
import sys
import time

import joblib
import numpy as np
import pandas as pd
import pyarrow.dataset as ds

from iaa_hackathon.baselines import BASE_FEATURES, score_vector
from iaa_hackathon.complexity_preflight import align_predictions
from iaa_hackathon.lightgbm_challenger import paired_uncertainty, report_pair, sha256
from iaa_hackathon.restricted_complexity import FEATURE, ContentsRefinement, promotion_decision
from iaa_hackathon.validation_scoring import score_supplied_predictions


ROOT = Path("outputs/step8")


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def relabel(obj):
    if isinstance(obj, list):
        return [relabel(value) for value in obj]
    if isinstance(obj, dict):
        names = {"glm": "benchmark", "lightgbm": "candidate"}
        return {names.get(key, key): names.get(value, value) if key == "model" and isinstance(value, str) else relabel(value) for key, value in obj.items()}
    return obj


def peak_memory_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def main() -> int:
    cfg_path = Path("configs/step8_complexity_gate.json")
    cfg = json.loads(cfg_path.read_text())
    out = Path(cfg["computational_budget"]["output_dir"])
    preflight = json.loads((ROOT / "preflight.json").read_text())
    if preflight["preflight_status"] != "ready":
        raise ValueError("benchmark preflight is not ready")
    benchmark_path = ROOT / "benchmark-frozen.json"
    diagnosis_path = ROOT / "diagnosis.json"
    frozen = json.loads(benchmark_path.read_text())
    diagnosis = json.loads(diagnosis_path.read_text())
    if sha256(benchmark_path) != cfg["benchmark_frozen_sha256"] or sha256(diagnosis_path) != cfg["diagnosis_sha256"]:
        raise ValueError("registered benchmark or diagnosis changed before fitting")
    if cfg["materiality"] != diagnosis["materiality"] or cfg["registered_at_ns"] <= diagnosis["completed_at_ns"]:
        raise ValueError("gate was not registered after diagnosis and before fitting")
    for name, value in frozen["artifacts_sha256"].items():
        if sha256(Path(name)) != value:
            raise ValueError(f"frozen S5-S7 evidence changed: {name}")
    code_paths = ["scripts/run_conditional_complexity.py", "scripts/step8_diagnosis.py", "src/iaa_hackathon/restricted_complexity.py", "src/iaa_hackathon/baselines.py", "src/iaa_hackathon/metrics.py", "src/iaa_hackathon/validation_scoring.py", "src/iaa_hackathon/lightgbm_challenger.py"]
    inputs = {"config_sha256": sha256(cfg_path), "benchmark_sha256": sha256(benchmark_path), "diagnosis_sha256": sha256(diagnosis_path), "code_sha256": {name: sha256(Path(name)) for name in code_paths}, "environment": {name: importlib.metadata.version(name) for name in ("numpy", "pandas", "scikit-learn", "pyarrow", "joblib")}, "python": platform.python_version()}
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        if previous.get("run_fingerprint") != fingerprint:
            raise ValueError("completed experiment has different provenance; preserve it and investigate")
        if all(sha256(out / name) == value for name, value in previous["artifacts_sha256"].items()) and sha256(ROOT / "decision.json") == previous["decision_sha256"]:
            print(json.dumps({"status": "reused_verified_run", "decision": json.loads((ROOT / "decision.json").read_text())["decision"]}))
            return 0
        raise ValueError("saved experiment artifact changed")
    for name in ("models", "predictions"):
        (out / name).mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    events = [{"event": "gate_registered", "at_ns": cfg["registered_at_ns"], "sha256": inputs["config_sha256"]}, {"event": "candidate_fit_started", "at_ns": time.time_ns()}]
    columns = sorted(set(["row_id", "customer_id", "customer_id_clean", "policy_id", "period_start", "line", "exposure_clean", "observed_net_incurred", "new_business", "cover_type", "occupancy", "driver_age", *BASE_FEATURES["contents"], "works_from_home", "lodgers", "bicycle_cover", "high_value_items"]))
    dataset = ds.dataset("outputs/step2/repairs/model/training-model-table.parquet")
    primary = dataset.to_table(columns=columns, filter=ds.field("period_start") < datetime(2024, 1, 1)).to_pandas()
    primary["period_year"] = pd.to_datetime(primary.period_start).dt.year
    train = primary[primary.period_year.isin([2021, 2022])]
    valid = primary[primary.period_year.eq(2023)].copy()
    versions = cfg["response_version"]
    settings = cfg["glm"]
    model = ContentsRefinement(cfg["benchmark_blocks"]["contents"], cfg["benchmark_features"]["contents"], alpha=settings["alpha"], max_iter=settings["max_iter"]).fit(train[train.line.eq("contents")])
    if not np.allclose(model.knots, cfg["candidate"]["primary_training_log_knots"], rtol=0, atol=1e-12):
        raise ValueError("training knots differ from registered transformation")

    def predict_and_save(fold, frame, fitted):
        baseline_path = Path(f"outputs/step6/features/predictions/{fold}-selected.parquet")
        if sha256(baseline_path) != cfg["benchmark_prediction_sha256"][fold]:
            raise ValueError("benchmark predictions changed")
        benchmark = align_predictions(frame, pd.read_parquet(baseline_path), fold=fold, response=versions)
        candidate = benchmark.copy()
        mask = frame.line.eq("contents").to_numpy()
        candidate[mask] = fitted.predict(frame.loc[mask])
        if not np.array_equal(candidate[~mask], benchmark[~mask]):
            raise ValueError("unaffected-line predictions changed")
        path = out / "models" / f"{fold}-contents.joblib"
        joblib.dump(fitted, path)
        restored = joblib.load(path)
        if not np.allclose(candidate[mask], restored.predict(frame.loc[mask]), rtol=1e-12, atol=1e-10):
            raise ValueError("saved candidate reload failed")
        original = joblib.load(f"outputs/step6/features/models/{fold}-contents-selected.joblib")
        previous_names = original.named_steps["transform"].get_feature_names_out().tolist()
        current_names = fitted.metadata["transformed_features"]
        extra = set(current_names) - set(previous_names)
        if extra != {f"numeric__{FEATURE}"} or len(current_names) != len(previous_names) + 1:
            raise ValueError("candidate introduced more than one coefficient")
        metadata = pd.DataFrame({"row_id": frame.row_id.to_numpy(), "fold_id": fold, "response_version": versions, "run_id": fingerprint, "prediction_unit": "policy_period_cost", "config_sha256": inputs["config_sha256"], "benchmark_sha256": inputs["benchmark_sha256"], "prediction": candidate})
        align_predictions(frame, metadata, fold=fold, response=versions)
        metadata.to_parquet(out / "predictions" / f"{fold}-candidate.parquet", index=False)
        scorer = score_supplied_predictions(frame[["row_id", "observed_net_incurred"]].rename(columns={"observed_net_incurred": "observed_net_baseline"}), metadata, fold_id=fold, response_version=versions)
        return benchmark, candidate, {"reload_equivalent": True, "other_lines_bitwise_unchanged": True, "additional_coefficients": len(extra), "model_bytes": path.stat().st_size, "fit": fitted.metadata, "step4_scorer": scorer}

    glm_primary, candidate_primary, primary_fit = predict_and_save("F2023", valid, model)
    selection = {"candidate_id": cfg["candidate"]["id"], "config_sha256": inputs["config_sha256"], "primary_model_sha256": sha256(out / "models/F2023-contents.joblib"), "primary_fit": primary_fit, "frozen_at_ns": time.time_ns(), "challenge_refit_rule": "same contents features/settings; knots refit from training-only 2021-2023 values"}
    write(out / "selection-frozen.json", selection)
    selection_sha = sha256(out / "selection-frozen.json")
    events.append({"event": "primary_specification_frozen", "at_ns": selection["frozen_at_ns"], "sha256": selection_sha})
    events.append({"event": "challenge_rows_first_loaded_for_candidate", "at_ns": time.time_ns()})
    challenge = dataset.to_table(columns=columns, filter=ds.field("period_start") >= datetime(2024, 1, 1)).to_pandas()
    challenge_model = ContentsRefinement(cfg["benchmark_blocks"]["contents"], cfg["benchmark_features"]["contents"], alpha=settings["alpha"], max_iter=settings["max_iter"]).fit(primary[primary.line.eq("contents")])
    glm_challenge, candidate_challenge, challenge_fit = predict_and_save("F2024", challenge, challenge_model)

    claims = pd.read_parquet("outputs/step2/repairs/claims/matched.parquet", columns=["claim_id", "matched_row_id", "line", "loss_date", "observed_net_incurred"])
    reports = {}
    risk_gain = []
    for fold, year, frame, training, baseline, candidate in (("F2023", 2023, valid, train, glm_primary, candidate_primary), ("F2024", 2024, challenge, primary, glm_challenge, candidate_challenge)):
        frame = frame.copy()
        frame["returning_customer"] = frame.customer_id_clean.isin(set(training.customer_id_clean))
        frame["returning_policy"] = frame.policy_id.isin(set(training.policy_id))
        report = relabel(report_pair(frame, baseline, candidate))
        report["uncertainty"] = paired_uncertainty(frame, baseline, candidate, seed=cfg["uncertainty"]["seed"], repeats=cfg["uncertainty"]["replicates"])
        report["by_line"] = {}
        for line in ("motor", "buildings", "contents"):
            mask = frame.line.eq(line).to_numpy()
            report["by_line"][line] = relabel(report_pair(frame.loc[mask], baseline[mask], candidate[mask]))
        mask = frame.line.eq("contents").to_numpy()
        edges = np.unique(np.quantile(training.loc[training.line.eq("contents"), "sum_insured_repaired"].dropna(), [0, .2, .4, .6, .8, 1]))
        edges[0], edges[-1] = -np.inf, np.inf
        bands = pd.cut(frame.loc[mask, "sum_insured_repaired"], edges, labels=False)
        report["contents_insured_bands"] = []
        for band in sorted(bands.dropna().unique()):
            local = bands.eq(band).to_numpy()
            subset = frame.loc[mask].loc[local]
            a, b = baseline[mask][local], candidate[mask][local]
            before, after = score_vector(subset.observed_net_incurred.to_numpy(float), a), score_vector(subset.observed_net_incurred.to_numpy(float), b)
            report["contents_insured_bands"].append({"band": int(band) + 1, "rows": len(subset), "benchmark": before, "candidate": after, "mean_deviance_gain": before["mean_tweedie_deviance"] - after["mean_tweedie_deviance"]})
        if fold == "F2023":
            risk_gain = report["contents_insured_bands"]
        include = np.ones(len(frame), dtype=bool)
        include[np.argsort(-frame.observed_net_incurred.to_numpy(float), kind="stable")[:10]] = False
        report["excluding_top10_observed"] = {"benchmark": score_vector(frame.loc[include, "observed_net_incurred"].to_numpy(float), baseline[include]), "candidate": score_vector(frame.loc[include, "observed_net_incurred"].to_numpy(float), candidate[include])}
        contents_claims = claims[claims.line.eq("contents") & pd.to_datetime(claims.loss_date).dt.year.eq(year)]
        largest = contents_claims.loc[contents_claims.observed_net_incurred.idxmax()]
        adjusted = frame.observed_net_incurred.to_numpy(float).copy()
        row = frame.row_id.eq(largest.matched_row_id).to_numpy()
        if row.sum() != 1:
            raise ValueError("largest contents claim does not map to one held-out row")
        adjusted[row] -= float(largest.observed_net_incurred)
        if (adjusted < 0).any():
            raise ValueError("claim sensitivity does not reconcile to the row response")
        report["largest_contents_claim_sensitivity"] = {"claim_id": largest.claim_id, "amount": float(largest.observed_net_incurred), "benchmark": score_vector(adjusted, baseline), "candidate": score_vector(adjusted, candidate), "primary_claim_retained": True}
        report["prediction_ratio_range"] = [float((candidate / baseline).min()), float((candidate / baseline).max())]
        reports[fold] = report
        write(out / f"{fold}-diagnostics.json", report)

    a, b = reports["F2023"], reports["F2024"]
    gain = a["uncertainty"]["mean_deviance_gain"]
    threshold = cfg["materiality"]["minimum_pooled_mean_deviance_gain"]
    noise_pass = gain > threshold and a["uncertainty"]["mean_deviance_gain_ci95"][0] > 0
    tail = next(row for row in a["tails"] if row["segment"] == "excluding_top_1pct_observed")
    top10 = a["excluding_top10_observed"]
    large = a["largest_contents_claim_sensitivity"]
    breadth = top10["candidate"]["mean_tweedie_deviance"] < top10["benchmark"]["mean_tweedie_deviance"] and tail["candidate"]["mean_tweedie_deviance"] < tail["benchmark"]["mean_tweedie_deviance"] and large["candidate"]["mean_tweedie_deviance"] < large["benchmark"]["mean_tweedie_deviance"] and sum(row["mean_deviance_gain"] > 0 for row in risk_gain) >= cfg["promotion_rules"]["2"]["minimum_contents_quantile_bands_with_positive_gain"]
    calibration_tolerance = cfg["promotion_rules"]["3"]["maximum_increase_absolute_AE_error_overall_and_per_line"]
    calibration = all(abs(row["candidate"]["A_over_E"] - 1) <= abs(row["benchmark"]["A_over_E"] - 1) + calibration_tolerance for report in reports.values() for row in [report["overall"], *[value["overall"] for value in report["by_line"].values()]])
    total_bounds = cfg["promotion_rules"]["4"]["overall_total_ratio_bounds"]
    ratio_bounds = cfg["promotion_rules"]["4"]["per_row_prediction_ratio_bounds"]
    totals_ok = all(total_bounds[0] <= report["overall"]["candidate"]["prediction_sum"] / report["overall"]["benchmark"]["prediction_sum"] <= total_bounds[1] and report["prediction_ratio_range"][0] >= ratio_bounds[0] and report["prediction_ratio_range"][1] <= ratio_bounds[1] for report in reports.values())
    elapsed, memory = time.perf_counter() - started, peak_memory_bytes()
    budget = cfg["promotion_rules"]["6"]
    proportional = elapsed <= budget["maximum_runtime_seconds"] and memory <= budget["maximum_peak_process_memory_bytes"] and primary_fit["additional_coefficients"] == challenge_fit["additional_coefficients"] == 1
    challenge_consistent = b["uncertainty"]["mean_deviance_gain"] >= -threshold
    if sha256(out / "selection-frozen.json") != selection_sha or sha256(cfg_path) != inputs["config_sha256"]:
        raise ValueError("selection or rule changed after challenge access")
    for name, value in frozen["artifacts_sha256"].items():
        if sha256(Path(name)) != value:
            raise ValueError(f"benchmark evidence changed during fitting: {name}")
    def gate(passed, detail):
        return {"status": "pass" if passed else "fail", "detail": detail}
    gates = {"1": gate(noise_pass, {"mean_deviance_gain": gain, "minimum_gain": threshold, "ci95": a["uncertainty"]["mean_deviance_gain_ci95"]}), "2": gate(breadth, {"positive_insured_bands": sum(row["mean_deviance_gain"] > 0 for row in risk_gain), "sensitivities": "top 10/top 1% removed separately and largest contents amount subtracted; primary retains claims"}), "3": gate(calibration, {"maximum_extra_absolute_AE_error": calibration_tolerance}), "4": gate(totals_ok, {"total_ratio_bounds": total_bounds, "row_ratio_bounds": ratio_bounds}), "5": gate(True, "frozen identities, exact IDs, one extra coefficient, training-only knots, unchanged other lines, direct Step 4 scoring and full reloads passed"), "6": gate(proportional, {"runtime_seconds": elapsed, "peak_process_memory_bytes": memory, "additional_coefficients": 1, "fits": 2}), "7": gate(challenge_consistent, {"challenge_mean_deviance_gain": b["uncertainty"]["mean_deviance_gain"], "allowed_uncertainty_tolerance": threshold, "challenge_evaluations": 1, "reused_development_challenge": True})}
    decision = promotion_decision(gates)
    events.append({"event": "challenge_evaluated_once", "at_ns": time.time_ns()})
    decision_record = {"step": 8, "status": "complete", "decision": decision, "benchmark": cfg["benchmark_model_id"], "candidate": cfg["candidate"]["id"], "benchmark_frozen_sha256": inputs["benchmark_sha256"], "config_sha256": inputs["config_sha256"], "run_fingerprint": fingerprint, "response_version": versions, "features": cfg["benchmark_features"], "new_feature": FEATURE, "scoring": cfg["scoring"], "folds": {fold: report["overall"] for fold, report in reports.items()}, "uncertainty": {fold: report["uncertainty"] for fold, report in reports.items()}, "promotion_gates": gates, "events": events, "runtime_seconds": elapsed, "peak_process_memory_bytes": memory, "candidate_fits": 2, "human_actuarial_review": "pending", "limitations": ["snapshot proxy and unresolved financial/IBNR/recovery assumptions", "sum-insured repair/exposure adoption pending", "F2024 reused development challenge", "bootstrap conditions on selected models and excludes target/search uncertainty", "risk-band diagnosis is exploratory; no causal interpretation", "official metric pooling/weights not verified"]}
    write(ROOT / "decision.json", decision_record)
    write(out / "results.json", {"folds": {fold: report["overall"] for fold, report in reports.items()}, "primary_fit": primary_fit, "challenge_fit": challenge_fit, "runtime_seconds": elapsed, "peak_process_memory_bytes": memory})
    artifacts = {str(path.relative_to(out)): sha256(path) for path in sorted(out.rglob("*")) if path.is_file() and path != manifest_path}
    write(manifest_path, {"status": "complete", "run_fingerprint": fingerprint, "inputs": inputs, "artifacts_sha256": artifacts, "decision_sha256": sha256(ROOT / "decision.json"), "candidate_fits": 2, "events": events, "selection_frozen_sha256": selection_sha, "runtime_seconds": elapsed, "peak_process_memory_bytes": memory})
    print(json.dumps({"status": "complete", "decision": decision, "runtime_seconds": elapsed, "peak_process_memory_bytes": memory, "promotion_gates": gates, "folds": decision_record["folds"]}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as exc:
        write(ROOT / "failure.json", {"status": "blocked", "error": f"{type(exc).__name__}: {exc}", "at_ns": time.time_ns()})
        raise
