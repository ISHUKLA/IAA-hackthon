"""Audit S5-S7 evidence and freeze the qualified Step 8 benchmark.

This module never trains models or interprets absent S7 evidence as a failed
challenger. Exit 2 means the preflight is blocked, not successful acceptance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
import shutil

import numpy as np
import pandas as pd

from iaa_hackathon.baselines import score_vector
from iaa_hackathon.validation_folds import membership_digest


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def align_predictions(expected: pd.DataFrame, supplied: pd.DataFrame, *, fold: str, response: str) -> np.ndarray:
    """Require exact IDs and metadata before using the existing scorer."""
    for frame in (expected, supplied):
        if frame.row_id.isna().any() or frame.row_id.duplicated().any():
            raise ValueError("row_id must be unique and non-null")
    if len(expected) != len(supplied) or set(expected.row_id) != set(supplied.row_id):
        raise ValueError("prediction IDs do not match the held-out fold")
    for column, value in (("fold_id", fold), ("response_version", response), ("prediction_unit", "policy_period_cost")):
        if column not in supplied or not supplied[column].eq(value).all():
            raise ValueError(f"incompatible {column}")
    prediction = supplied.set_index("row_id").loc[expected.row_id, "prediction"].to_numpy(float)
    if not np.isfinite(prediction).all() or (prediction <= 0).any():
        raise ValueError("predictions must be finite and strictly positive")
    return prediction


def prerequisite_decision(step7_manifests: list[str], errors: list[str], *, step7_verified: bool = False) -> tuple[str, list[str]]:
    blockers = list(errors)
    if not step7_manifests:
        blockers.append("missing_step7_evidence: no local Step 7 experiment manifest, predictions, fitted models or acceptance report")
    elif not step7_verified:
        blockers.append("step7_evidence_requires_review: integrate and verify the discovered artifacts before qualifying the Step 8 benchmark")
    return ("blocked" if blockers else "ready"), blockers


def main() -> int:
    started = time.perf_counter()
    root = Path.cwd()
    read = lambda path: json.loads((root / path).read_text())
    frozen: dict[str, str] = {}
    errors: list[str] = []
    checks: list[dict] = []
    evidence: dict = {"S5": [], "S6": []}
    step7_verified = False

    def record(name: str, condition: bool) -> None:
        checks.append({"check": name, "status": "pass" if condition else "fail"})
        if not condition:
            errors.append(name)

    def identity(path: str, expected: str | None = None) -> str:
        digest = sha256(root / path)
        frozen[path] = digest
        if expected is not None:
            record(f"sha256:{path}", digest == expected)
        return digest

    try:
        gate = read("configs/step8_complexity_gate.json")
        audit = read("outputs/step2/repairs/repair-audit.json")
        s5 = read("outputs/step5/baselines/manifest.json")
        s6 = read("outputs/step6/features/manifest.json")
        s7 = read("outputs/step7/manifest.json")
        s7_acceptance = read("outputs/step7/acceptance.json")
        s7_decision = read("outputs/step7/decision.json")
        s7_config = read("configs/step7_lightgbm.json")
        views = read("outputs/step4/repaired-views/manifest.json")
        validation = read("configs/validation.json")
        for path, digest in audit["outputs"].items():
            identity(f"outputs/step2/repairs/{path}", digest)
        audit_hash = identity("outputs/step2/repairs/repair-audit.json", s5["inputs"]["repair_audit"])
        model_hash = frozen["outputs/step2/repairs/model/training-model-table.parquet"]
        claim_hash = frozen["outputs/step2/repairs/claims/matched.parquet"]
        record("S4/S5/S6 repaired input universe", model_hash == s5["inputs"]["training_model_table"] == s6["input_sha256"] == views["inputs"]["policy"])
        record("repaired claim/reporting universe", claim_hash == views["inputs"]["matched_claims"] and audit_hash == views["inputs"]["repair_audit"])
        record("S5/S6 response version", s5["response_version"] == s6["response_version"] == gate["response_version"])
        record("snapshot proxy mode", s5["experiment_mode"] == s6["experiment_mode"] == views["experiment_mode"] == gate["experiment_mode"])
        record("S5/S6 completed manifests", s5["status"] == s6["status"] == "complete")
        record("S7 completed and accepted", s7["status"] == "complete" and s7_acceptance["status"] == "passed")
        record("S7 retains S6 benchmark", s7_decision["decision"] == "glm_preferred_for_step8" and s7_decision["benchmark"] == "S6_selected_compact_tweedie_glm")
        record("S7 repaired universe and response", s7["inputs"]["policy"] == model_hash and s7["inputs"]["claims"] == claim_hash and s7["response_version"] == s6["response_version"])
        record("S7 same feature blocks", s7["blocks"] == s6["selected_blocks"])
        record("S7 period/rate formulation", s7["rate_formulation"]["power"] == 1.5 and s7["rate_formulation"]["metric_weights"] == "none" and s7["rate_formulation"]["floor"] is None)
        identity("configs/step7_lightgbm.json", s7["config"])
        for path, digest in s7["code"].items():
            identity(path, digest)
        for path, digest in s7["artifacts_sha256"].items():
            identity(f"outputs/step7/{path}", digest)
        for path in ("outputs/step7/manifest.json", "outputs/step7/acceptance.json", "outputs/step7/preflight.json"):
            identity(path)
        events = {item["event"]: item["at_ns"] for item in s7["events"]}
        record("S7 selection frozen before reused challenge", s7["challenge_evaluations"] == 1 and events["selection_frozen"] < events["challenge_rows_first_loaded_for_lightgbm"] < events["challenge_evaluated_once"])
        identity("configs/baselines.json", s5["inputs"]["config"])
        identity("configs/features.json", s6["config_sha256"])
        for manifest, runner in ((s5, "run_baselines.py"), (s6, "run_feature_experiments.py")):
            identity("src/iaa_hackathon/baselines.py", manifest["code_sha256"]["baselines.py"])
            identity(f"scripts/{runner}", manifest["code_sha256"][runner])
        for path in ("configs/validation.json", "configs/feature_registry.json", "configs/step8_complexity_gate.json", "prompts/step8/00-conditional-complexity.md", "src/iaa_hackathon/metrics.py", "src/iaa_hackathon/validation_scoring.py", "src/iaa_hackathon/complexity_preflight.py", "outputs/step5/baselines/manifest.json", "outputs/step6/features/manifest.json", "outputs/step4/repaired-views/manifest.json", "outputs/step6/features/diagnostics.json"):
            identity(path)
        identity("outputs/step4/folds/fold-membership.parquet")
        record("S7 same frozen membership bytes", frozen["outputs/step4/folds/fold-membership.parquet"] == s7["inputs"]["fold_membership"])
        membership = None
        try:
            membership = pd.read_parquet(root / "outputs/step4/folds/fold-membership.parquet")
        except (OSError, ValueError) as exc:
            record(f"unreadable frozen folds: outputs/step4/folds/fold-membership.parquet: {type(exc).__name__}: {exc}", False)
        if membership is not None:
            record("Step 4 membership digest", membership_digest(membership) == read("outputs/step4/folds/fold-summary.json")["membership_digest"])
        data = pd.read_parquet(root / "outputs/step2/repairs/model/training-model-table.parquet", columns=["row_id", "period_start", "exposure_clean", "observed_net_incurred"])
        data["period_year"] = pd.to_datetime(data.period_start).dt.year
        record("model table unique non-null IDs", not data.row_id.isna().any() and not data.row_id.duplicated().any())
        record("positive finite exposure", bool(np.isfinite(data.exposure_clean).all() and (data.exposure_clean > 0).all()))
        s5_results = read("outputs/step5/baselines/results.json")
        s6_results = read("outputs/step6/features/results.json")
        for path in ("outputs/step5/baselines/results.json", "outputs/step6/features/results.json"):
            identity(path)
        for fold in (item for item in validation["folds"] if item["id"] in ("F2023", "F2024")):
            fold_id = fold["id"]
            valid = data[data.period_year.eq(fold["validation_year"])].copy()
            for role, expected in (("train", data[data.period_year.isin(fold["train_years"])]), ("validation", valid)):
                if membership is None:
                    checks.append({"check": f"{fold_id} exact {role} membership", "status": "not_testable", "reason": "saved membership Parquet is unreadable"})
                else:
                    observed = membership[membership.fold_id.eq(fold_id) & membership.role.eq(role)]
                    record(f"{fold_id} exact {role} membership", len(observed) == len(expected) and set(observed.row_id) == set(expected.row_id))
            identity(f"outputs/step4/repaired-views/responses/{fold_id}.parquet", views["folds"][fold_id]["response_sha256"])
            identity(f"outputs/step4/repaired-views/reporting/{fold_id}-fits.json", views["folds"][fold_id]["reporting_sha256"])
            response = pd.read_parquet(root / f"outputs/step4/repaired-views/responses/{fold_id}.parquet", columns=["row_id", "observed_net_baseline", "exposure_clean"], filters=[("role", "==", "validation")]).set_index("row_id")
            record(f"{fold_id} S4 response alias reconciles to S5-S7", set(response.index) == set(valid.row_id) and np.allclose(response.loc[valid.row_id, "observed_net_baseline"], valid.observed_net_incurred, rtol=0, atol=1e-8) and np.array_equal(response.loc[valid.row_id, "exposure_clean"].to_numpy(), valid.exposure_clean.to_numpy()))
            for stage, path, rows in (("S5", f"outputs/step5/baselines/predictions/{fold_id}-B3_compact_tweedie_glm.parquet", s5_results), ("S6", f"outputs/step6/features/predictions/{fold_id}-selected.parquet", s6_results)):
                prediction = align_predictions(valid, pd.read_parquet(root / path), fold=fold_id, response=gate["response_version"])
                identity(path)
                actual = score_vector(valid.observed_net_incurred.to_numpy(float), prediction)
                saved = next(row for row in rows if row["fold_id"] == fold_id and (row.get("model_id") == "B3_compact_tweedie_glm" and row.get("scope") == "pooled" if stage == "S5" else row.get("line") == "pooled"))
                record(f"{fold_id} {stage} saved score reproduced", bool(np.isclose(actual["mean_tweedie_deviance"], saved["mean_tweedie_deviance"], rtol=1e-12, atol=1e-12) and np.isclose(actual["d2_tweedie_score"], saved["d2_tweedie_score"], rtol=1e-12, atol=1e-12)))
                evidence[stage].append({"fold_id": fold_id, **actual})
            s7_prediction = align_predictions(valid, pd.read_parquet(root / f"outputs/step7/predictions/{fold_id}-selected.parquet"), fold=fold_id, response=gate["response_version"])
            measured = score_vector(valid.observed_net_incurred.to_numpy(float), s7_prediction)
            recorded = read(f"outputs/step7/{fold_id}-diagnostics.json")["overall"]["lightgbm"]
            record(f"{fold_id} S7 saved score reproduced", bool(np.isclose(measured["mean_tweedie_deviance"], recorded["mean_tweedie_deviance"], rtol=1e-12, atol=1e-12)))
            evidence.setdefault("S7", []).append({"fold_id": fold_id, **measured})
        for directory in ("outputs/step5/baselines/models", "outputs/step6/features/models"):
            files = sorted((root / directory).glob("*.joblib"))
            record(f"saved models present:{directory}", bool(files))
            for path in files:
                identity(str(path.relative_to(root)))
        evidence["S6_features"] = {row["line"]: row["features"] for row in s6_results if row.get("fold_id") == "F2023" and row.get("candidate") == "selected_combined" and row["line"] != "pooled"}
        evidence["S6_line_scores"] = [row for row in s6_results if row.get("candidate") in ("selected_combined", "frozen_selected") and row["line"] != "pooled"]
        evidence["recorded_runtime_seconds"] = {"S5": s5["runtime"]["total_seconds"], "S6": s6["runtime_seconds"]}
        record("S6/S7 exact predictor lists", evidence["S6_features"] == s7["features"])
        evidence["S6_settings"] = read("configs/baselines.json")["glm"]
        evidence["S6_blocks"] = s6["selected_blocks"]
        evidence["S7_decision"] = s7_decision
        step7_verified = not errors
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        errors.append(f"evidence_unavailable_or_incompatible: {type(exc).__name__}: {exc}")

    step7_paths = ("outputs/step7", "docs/step7", "reports/step7", "prompts/step7")
    step7_files = sorted(str(path.relative_to(root)) for name in step7_paths for path in (root / name).rglob("*") if path.is_file())
    step7_manifests = [path for path in step7_files if Path(path).name.endswith("manifest.json")]
    decision, blockers = prerequisite_decision(step7_manifests, errors, step7_verified=step7_verified)
    result = {
        "step": 8,
        "decision": decision,
        "preflight_status": decision,
        "blockers": blockers,
        "available_benchmark": "S6_selected_compact_tweedie_glm" if evidence["S6"] else None,
        "benchmark_fully_verified": not errors,
        "benchmark_qualified_against_step7": step7_verified,
        "candidate": None,
        "candidate_fits": 0,
        "promotion_gates": {str(i): {"status": "not_testable", "reason": "Step 7 prerequisite missing or unverified; no candidate registered or fitted"} for i in range(1, 8)},
        "checks": checks,
        "step7_search_roots": list(step7_paths),
        "step7_files": step7_files,
        "frozen_available_artifacts_sha256": frozen,
        "existing_evidence_reverified": evidence,
        "uncertainty_estimates": None,
        "challenge_status": "reused development challenge; prior S5/S6 results only",
        "limitations": ["historical scorer hashes were not stored by S5/S6; S7 recorded the current scorer and saved predictions were rescored", "S6/S7 full reload equivalence previously passed S7 actual acceptance and artifact identities were reverified", "preflight peak memory not measured", "ultimate/IBNR, recoveries, financial basis, exposure and sum-insured adoption remain pending"],
        "preflight_seconds": time.perf_counter() - started,
        "reproduce": "make step8-preflight PYTHON=.venv/bin/python",
    }
    output_dir = root / "outputs/step8"
    output_dir.mkdir(parents=True, exist_ok=True)
    previous = output_dir / "decision.json"
    if previous.exists() and json.loads(previous.read_text()).get("decision") == "blocked":
        history = output_dir / "history"
        history.mkdir(exist_ok=True)
        shutil.copy2(previous, history / f"blocked-{sha256(previous)}.json")
    (output_dir / "preflight.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    if decision == "ready":
        # The experiment gate and audit timestamps are not benchmark inputs.
        audit_only = {"configs/step8_complexity_gate.json", "src/iaa_hackathon/complexity_preflight.py", "outputs/step7/preflight.json"}
        snapshot = {"benchmark_id": result["available_benchmark"], "response_version": gate["response_version"], "features": evidence["S6_features"], "settings": evidence["S6_settings"], "blocks": evidence["S6_blocks"], "folds": validation["folds"], "scoring": read("configs/problem_contract.json")["metric"], "artifacts_sha256": {path: digest for path, digest in frozen.items() if path not in audit_only}}
        snapshot_path = output_dir / "benchmark-frozen.json"
        previous_snapshot = json.loads(snapshot_path.read_text()) if snapshot_path.exists() else {}
        if {key: value for key, value in previous_snapshot.items() if key != "frozen_at_ns"} != snapshot:
            snapshot["frozen_at_ns"] = time.time_ns()
            snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n")
    else:
        (output_dir / "decision.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"preflight_status": decision, "checks_passed": sum(item["status"] == "pass" for item in checks), "checks_failed": sum(item["status"] == "fail" for item in checks), "blockers": blockers, "candidate_fits": 0, "output": "outputs/step8/preflight.json"}, indent=2))
    return 0 if decision == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
