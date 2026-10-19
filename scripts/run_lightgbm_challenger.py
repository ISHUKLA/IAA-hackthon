"""Execute S7 Phase A, freeze on F2023, and evaluate F2024 once."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

import lightgbm as lgb
import numpy as np
import pandas as pd
import pyarrow.dataset as ds

from iaa_hackathon.baselines import BASE_FEATURES, score_vector
from iaa_hackathon.complexity_preflight import align_predictions
from iaa_hackathon.lightgbm_challenger import FeaturePipeline, assert_identity, fit_model, paired_uncertainty, period_prediction, report_pair, sha256


def write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def peak_memory_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def explain(model, pipeline, training, validation, out, prefix, settings):
    sample = validation.sort_values("row_id").head(settings["out_of_sample_rows"]).copy()
    matrix = pipeline.transform(sample)
    contributions = model.predict(matrix, pred_contrib=True, num_threads=4)
    raw = model.predict(matrix, raw_score=True, num_threads=4)
    if not np.allclose(contributions.sum(axis=1), raw, rtol=1e-10, atol=1e-10):
        raise ValueError("native TreeSHAP does not reconcile to log-rate prediction")
    names = model.feature_name()
    gain = model.feature_importance(importance_type="gain")
    split = model.feature_importance(importance_type="split")
    importance = [{"feature": name, "gain": float(a), "split": int(b), "mean_abs_native_shap_log_rate": float(np.abs(contributions[:, i]).mean())} for i, (name, a, b) in enumerate(zip(names, gain, split))]
    shap = pd.DataFrame(contributions, columns=[*names, "expected_log_rate"])
    shap.insert(0, "row_id", sample.row_id.to_numpy())
    shap.to_parquet(out / "explanations" / f"{prefix}-native-shap.parquet", index=False)
    dependence = []
    for index in np.argsort(-gain):
        feature = names[index]
        if feature not in training or not pd.api.types.is_numeric_dtype(training[feature]) or training[feature].nunique() < 5:
            continue
        grid = np.unique(np.quantile(training[feature].dropna().to_numpy(float), [.1, .25, .5, .75, .9]))
        for value in grid:
            altered = sample.copy()
            altered[feature] = value
            dependence.append({"feature": feature, "value": float(value), "mean_period_prediction": float(period_prediction(model, pipeline, altered).mean()), "sample_rows": len(sample)})
        break
    write(out / "explanations" / f"{prefix}.json", {"importance": importance, "native_tree_shap_rows": len(sample), "shap_additivity_verified": True, "shap_scale": "log annual rate; expected value included", "partial_dependence": dependence, "interpretation": "model behaviour only; no causal or availability claim"})


def save_model(model, pipeline, out, prefix, valid, prediction):
    model_path = out / "models" / f"{prefix}.txt"
    model.save_model(model_path, num_iteration=model.best_iteration or model.current_iteration())
    pipeline_path = out / "models" / f"{prefix}-pipeline.json"
    write(pipeline_path, {"line": pipeline.line, "blocks": pipeline.blocks, "allowed": pipeline.allowed, "vocabularies": pipeline.vocabularies})
    reloaded = lgb.Booster(model_file=str(model_path))
    restored = FeaturePipeline(**json.loads(pipeline_path.read_text()))
    if not np.allclose(prediction, period_prediction(reloaded, restored, valid), rtol=1e-12, atol=1e-10):
        raise ValueError(f"saved model reload mismatch: {prefix}")
    return {"model_bytes": model_path.stat().st_size, "reload_equivalent": True, "model_sha256": sha256(model_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/step7_lightgbm.json"))
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    out = Path(cfg["outputs"])
    for name in ("models", "predictions", "explanations"):
        (out / name).mkdir(parents=True, exist_ok=True)
    preflight = json.loads((out / "preflight.json").read_text())
    if preflight["status"] != "passed":
        raise ValueError("Step 7 preflight has not passed")
    policy = Path("outputs/step2/repairs/model/training-model-table.parquet")
    claims_path = Path("outputs/step2/repairs/claims/matched.parquet")
    inputs = {"policy": sha256(policy), "claims": sha256(claims_path), "fold_membership": sha256(Path("outputs/step4/folds/fold-membership.parquet")), "S6_manifest": sha256(Path("outputs/step6/features/manifest.json"))}
    assert_identity(inputs, {"policy": cfg["input_policy_sha256"], "claims": cfg["matched_claims_sha256"], "fold_membership": preflight["fold_membership_sha256"]})
    assert_identity(preflight, {"fold_membership_digest": cfg["fold_membership_digest"], "response_version": cfg["response_version"]})
    code_paths = ["src/iaa_hackathon/lightgbm_challenger.py", "scripts/run_lightgbm_challenger.py", "scripts/step7_preflight.py", "src/iaa_hackathon/baselines.py", "src/iaa_hackathon/metrics.py", "src/iaa_hackathon/validation_scoring.py", "src/iaa_hackathon/validation_folds.py"]
    code_hashes = {path: sha256(Path(path)) for path in code_paths}
    environment = {name: importlib.metadata.version(name) for name in ("lightgbm", "numpy", "pandas", "scikit-learn", "pyarrow", "scipy", "joblib")}
    environment["python"] = platform.python_version()
    for name, version in cfg["environment"].items():
        if environment[name] != version:
            raise ValueError(f"untested software version: {name}")
    fingerprint_payload = {"inputs": inputs, "config": sha256(args.config), "code": code_hashes, "environment": environment, "benchmark_predictions": cfg["benchmark_prediction_sha256"]}
    fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True).encode()).hexdigest()
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        if previous.get("run_fingerprint") == fingerprint and previous.get("status") == "complete":
            if all(sha256(out / name) == digest for name, digest in previous["artifacts_sha256"].items()):
                print(json.dumps({"status": "reused_verified_run", "decision": json.loads((out / "decision.json").read_text())["decision"]}))
                return 0
            raise ValueError("existing run artifact changed; preserve and investigate before refitting")
        raise ValueError("existing run has different provenance; select a new output directory instead of overwriting")

    started = time.perf_counter()
    events = [{"event": "preflight_verified", "at_ns": time.time_ns()}]
    feature_cfg = json.loads(Path("configs/features.json").read_text())
    source = set(sum(BASE_FEATURES.values(), []))
    for line, blocks in cfg["blocks"].items():
        for block in blocks:
            source.update(feature_cfg["blocks"][line][block]["source"])
    columns = ["row_id", "policy_id", "customer_id", "customer_id_clean", "period_start", "line", "new_business", "exposure_clean", "observed_net_incurred", *sorted(source)]
    dataset = ds.dataset(policy, format="parquet")

    def load_years(years):
        # Physical filtering keeps future financial rows out of the primary run.
        condition = (ds.field("period_start") >= datetime(min(years), 1, 1)) & (ds.field("period_start") < datetime(max(years) + 1, 1, 1))
        data = dataset.to_table(columns=columns, filter=condition).to_pandas()
        data["period_year"] = pd.to_datetime(data.period_start).dt.year
        return data

    primary = load_years([2021, 2022, 2023])
    train_all = primary[primary.period_year.isin([2021, 2022])]
    valid_all = primary[primary.period_year.eq(2023)].copy()
    baseline_path = Path("outputs/step6/features/predictions/F2023-selected.parquet")
    if sha256(baseline_path) != cfg["benchmark_prediction_sha256"]["F2023"]:
        raise ValueError("S6 primary predictions changed")
    glm_primary = align_predictions(valid_all, pd.read_parquet(baseline_path), fold="F2023", response=cfg["response_version"])
    search = []
    selected = {}
    primary_prediction = np.empty(len(valid_all))
    selected_models = {}
    pilot = None

    def save_predictions(frame, prediction, name, fold_id):
        pd.DataFrame({"row_id": frame.row_id.to_numpy(), "fold_id": fold_id, "response_version": cfg["response_version"], "run_id": fingerprint, "config_sha256": fingerprint_payload["config"], "input_policy_sha256": inputs["policy"], "prediction_unit": "policy_period_cost", "prediction": prediction}).to_parquet(out / "predictions" / f"{name}.parquet", index=False)

    for line in ("motor", "buildings", "contents"):
        training = train_all[train_all.line.eq(line)]
        valid = valid_all[valid_all.line.eq(line)]
        mask = valid_all.line.eq(line).to_numpy()
        benchmark = score_vector(valid.observed_net_incurred.to_numpy(float), glm_primary[mask])
        best = None
        fit_seconds = 0.0
        for candidate in cfg["candidates"]:
            params = {**cfg["shared_params"], **{k: v for k, v in candidate.items() if k != "id"}}
            name = f"F2023-{line}-{candidate['id']}"
            try:
                model, pipeline, meta = fit_model(training, valid, line=line, blocks=cfg["blocks"][line], features=cfg["features"][line], params=params, rounds=cfg["round_cap"], early_stopping_rounds=cfg["early_stopping_rounds"])
                prediction = period_prediction(model, pipeline, valid)
                scores = score_vector(valid.observed_net_incurred.to_numpy(float), prediction)
                saved = save_model(model, pipeline, out, name, valid, prediction)
                save_predictions(valid, prediction, name, "F2023")
                attempt = {"line": line, "candidate": candidate["id"], "status": "trained", "params": params, "metadata": meta, "scores": scores, "glm_mean_deviance": benchmark["mean_tweedie_deviance"], "delta_mean_deviance": scores["mean_tweedie_deviance"] - benchmark["mean_tweedie_deviance"], "peak_process_memory_bytes_so_far": peak_memory_bytes(), **saved}
                search.append(attempt)
                write(out / "search-history.json", search)
                fit_seconds += meta["seconds"]
                previous_best = best[0] if best is not None else benchmark["mean_tweedie_deviance"]
                gain = previous_best - scores["mean_tweedie_deviance"]
                if best is None or scores["mean_tweedie_deviance"] < best[0]:
                    best = (scores["mean_tweedie_deviance"], candidate, model, pipeline, meta, prediction)
                if pilot is None:
                    pilot = {"line": line, "configuration": candidate, "fit_seconds": meta["seconds"], "peak_process_memory_bytes": peak_memory_bytes(), "maximum_candidates_per_line": 3 if meta["seconds"] <= cfg["resources"]["pilot_seconds_limit_for_expansion"] else 1, "predeclared_candidates": cfg["candidates"]}
                    write(out / "pilot-budget.json", pilot)
                print(json.dumps({"phase": "primary", "line": line, "candidate": candidate["id"], "mean_deviance": scores["mean_tweedie_deviance"], "GLM": benchmark["mean_tweedie_deviance"], "rounds": meta["best_iteration"], "seconds": meta["seconds"]}), flush=True)
                if len([row for row in search if row["line"] == line]) >= pilot["maximum_candidates_per_line"] or fit_seconds >= cfg["resources"]["maximum_training_seconds_per_line"]:
                    break
                if gain / benchmark["mean_tweedie_deviance"] < cfg["resources"]["extra_candidates_only_if_relative_deviance_gain_at_least"]:
                    break
            except (ValueError, lgb.basic.LightGBMError) as exc:
                search.append({"line": line, "candidate": candidate["id"], "status": "failed", "error": str(exc)})
                write(out / "search-history.json", search)
        if best is None:
            raise ValueError(f"all candidates failed for {line}")
        _, candidate, model, pipeline, meta, prediction = best
        selected[line] = {"candidate": candidate, "rounds": meta["best_iteration"], "features": cfg["features"][line], "blocks": cfg["blocks"][line]}
        primary_prediction[mask] = prediction
        selected_models[line] = (model, pipeline)
        save_model(model, pipeline, out, f"F2023-{line}-selected", valid, prediction)
        explain(model, pipeline, training, valid, out, f"F2023-{line}", cfg["explanations"])
    save_predictions(valid_all, primary_prediction, "F2023-selected", "F2023")
    freeze = {"frozen_at_ns": time.time_ns(), "run_fingerprint": fingerprint, "selection": selected, "selection_fold": "F2023", "challenge_accessed": False}
    write(out / "selection-frozen.json", freeze)
    frozen_sha = sha256(out / "selection-frozen.json")
    events.append({"event": "selection_frozen", "at_ns": freeze["frozen_at_ns"], "sha256": frozen_sha})

    # The candidate and tree counts are frozen before this first challenge read.
    events.append({"event": "challenge_rows_first_loaded_for_lightgbm", "at_ns": time.time_ns()})
    challenge = load_years([2024])
    challenge_prediction = np.empty(len(challenge))
    challenge_fits = []
    for line, spec in selected.items():
        training = primary[primary.line.eq(line)]
        valid = challenge[challenge.line.eq(line)]
        params = {**cfg["shared_params"], **{k: v for k, v in spec["candidate"].items() if k != "id"}}
        model, pipeline, meta = fit_model(training, None, line=line, blocks=spec["blocks"], features=spec["features"], params=params, rounds=spec["rounds"])
        prediction = period_prediction(model, pipeline, valid)
        challenge_prediction[challenge.line.eq(line).to_numpy()] = prediction
        saved = save_model(model, pipeline, out, f"F2024-{line}-selected", valid, prediction)
        challenge_fits.append({"line": line, "params": params, "metadata": meta, **saved})
    save_predictions(challenge, challenge_prediction, "F2024-selected", "F2024")
    baseline_path = Path("outputs/step6/features/predictions/F2024-selected.parquet")
    if sha256(baseline_path) != cfg["benchmark_prediction_sha256"]["F2024"]:
        raise ValueError("S6 challenge predictions changed")
    glm_challenge = align_predictions(challenge, pd.read_parquet(baseline_path), fold="F2024", response=cfg["response_version"])
    claims = pd.read_parquet(claims_path, columns=["claim_id", "matched_row_id", "line", "peril", "loss_date", "observed_net_incurred"])
    reports = {}
    for fold_id, year, validation, glm, prediction in (("F2023", 2023, valid_all, glm_primary, primary_prediction), ("F2024", 2024, challenge, glm_challenge, challenge_prediction)):
        train_years = train_all if year == 2023 else primary
        validation = validation.copy()
        validation["returning_policy"] = validation.policy_id.isin(set(train_years.policy_id))
        validation["returning_customer"] = validation.customer_id_clean.isin(set(train_years.customer_id_clean))
        report = report_pair(validation, glm, prediction)
        report["uncertainty"] = paired_uncertainty(validation, glm, prediction, seed=cfg["uncertainty"]["seed"], repeats=cfg["uncertainty"]["replicates"])
        report["by_line"] = {}
        for line in selected:
            mask = validation.line.eq(line).to_numpy()
            report["by_line"][line] = report_pair(validation.loc[mask], glm[mask], prediction[mask])
        bi = claims[claims.line.eq("motor") & claims.peril.eq("bodily_injury") & pd.to_datetime(claims.loss_date).dt.year.eq(year)]
        largest = bi.loc[bi.observed_net_incurred.idxmax()]
        adjusted = validation.copy()
        mask = adjusted.row_id.eq(largest.matched_row_id)
        if mask.sum() != 1:
            raise ValueError("BI sensitivity does not map to exactly one row")
        amount = float(largest.observed_net_incurred)
        adjusted.loc[mask, "observed_net_incurred"] -= amount
        if (adjusted.observed_net_incurred < -1e-8).any():
            raise ValueError("BI sensitivity violates response reconciliation")
        report["largest_BI_sensitivity"] = {"claim_id": largest.claim_id, "amount": amount, "glm": score_vector(adjusted.observed_net_incurred.to_numpy(float), glm), "lightgbm": score_vector(adjusted.observed_net_incurred.to_numpy(float), prediction), "primary_claim_retained": True}
        reports[fold_id] = report
        write(out / f"{fold_id}-diagnostics.json", report)
    primary_report, challenge_report = reports["F2023"], reports["F2024"]
    rules = cfg["decision_rules"]
    calibration_ok = all(abs(row["overall"]["lightgbm"]["A_over_E"] - 1) <= abs(row["overall"]["glm"]["A_over_E"] - 1) + rules["maximum_increase_in_absolute_AE_error_per_line"] for report in reports.values() for row in report["by_line"].values())
    tails = next(row for row in primary_report["tails"] if row["segment"] == "excluding_top_1pct_observed")
    gates = {"primary_paired_ci_positive": primary_report["uncertainty"]["mean_deviance_gain_ci95"][0] > 0, "challenge_direction_positive": challenge_report["uncertainty"]["mean_deviance_gain"] > 0, "major_line_calibration": calibration_ok, "gain_outside_top_1pct": tails["lightgbm"]["mean_tweedie_deviance"] < tails["glm"]["mean_tweedie_deviance"], "gain_after_largest_BI_sensitivity": primary_report["largest_BI_sensitivity"]["lightgbm"]["mean_tweedie_deviance"] < primary_report["largest_BI_sensitivity"]["glm"]["mean_tweedie_deviance"]}
    if all(gates.values()):
        decision = "lightgbm_preferred_for_step8"
    elif primary_report["uncertainty"]["mean_deviance_gain"] <= 0 or challenge_report["uncertainty"]["mean_deviance_gain"] <= 0:
        decision = "glm_preferred_for_step8"
    else:
        decision = "inconclusive"
    events.append({"event": "challenge_evaluated_once", "at_ns": time.time_ns()})
    if sha256(out / "selection-frozen.json") != frozen_sha:
        raise ValueError("selection changed after challenge access")
    for path, value in fingerprint_payload["inputs"].items():
        actual = {"policy": policy, "claims": claims_path, "fold_membership": Path("outputs/step4/folds/fold-membership.parquet"), "S6_manifest": Path("outputs/step6/features/manifest.json")}[path]
        if sha256(actual) != value:
            raise ValueError(f"upstream changed during execution: {path}")
    write(out / "results.json", {"folds": {key: value["overall"] for key, value in reports.items()}, "challenge_fits": challenge_fits, "search_attempts": len(search), "selected": selected})
    write(out / "decision.json", {"decision": decision, "benchmark": cfg["benchmark_model_id"], "challenger": "S7_Phase_A_LightGBM", "run_fingerprint": fingerprint, "gates": gates, "primary_uncertainty": primary_report["uncertainty"], "challenge_uncertainty": challenge_report["uncertainty"], "response_version": cfg["response_version"], "challenge_status": cfg["challenge_status"], "limitations": ["snapshot proxy, not ultimate outcomes", "financial basis, IBNR, recovery, exposure and sum-insured adoption pending", "repaired scenario sensitivity unavailable", "F2024 reused development challenge", "no new features in Phase A", "native TreeSHAP describes log-rate model behaviour"]})
    artifacts = {str(path.relative_to(out)): sha256(path) for path in sorted(out.rglob("*")) if path.is_file() and path != manifest_path and "fold-recovery" not in path.parts and path.name != "preflight.json"}
    git = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), "status_porcelain": subprocess.check_output(["git", "status", "--porcelain"], text=True)}
    manifest = {"status": "complete", "stage": "S7", "run_fingerprint": fingerprint, **fingerprint_payload, "response_version": cfg["response_version"], "scenario": cfg["scenario"], "claim_universe": cfg["claim_universe"], "fold_membership_digest": cfg["fold_membership_digest"], "features": cfg["features"], "blocks": cfg["blocks"], "rate_formulation": cfg["rate_formulation"], "selection_frozen_sha256": frozen_sha, "events": events, "git": git, "runtime_seconds": time.perf_counter() - started, "peak_process_memory_bytes": peak_memory_bytes(), "artifacts_sha256": artifacts, "challenge_evaluations": 1, "phase_B": "not_executed"}
    write(manifest_path, manifest)
    print(json.dumps({"status": "complete", "decision": decision, "gates": gates, "runtime_seconds": manifest["runtime_seconds"], "peak_process_memory_bytes": manifest["peak_process_memory_bytes"], "folds": {key: value["overall"] for key, value in reports.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, lgb.basic.LightGBMError) as exc:
        output = Path("outputs/step7")
        output.mkdir(parents=True, exist_ok=True)
        write(output / "failure.json", {"status": "blocked", "error": f"{type(exc).__name__}: {exc}", "at_ns": time.time_ns()})
        raise
