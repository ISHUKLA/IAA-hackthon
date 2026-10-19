"""Recover the frozen fold artifact and verify the saved S6 benchmark."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import time

import joblib
import numpy as np
import pandas as pd

from iaa_hackathon.baselines import BASE_FEATURES, add_feature_blocks
from iaa_hackathon.complexity_preflight import align_predictions
from iaa_hackathon.lightgbm_challenger import assert_identity, sha256
from iaa_hackathon.metrics import metric_report
from iaa_hackathon.validation_folds import build_membership, membership_digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/step7"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path("configs/validation.json").read_text())
    audit = json.loads(Path("outputs/step2/repairs/repair-audit.json").read_text())
    s6 = json.loads(Path("outputs/step6/features/manifest.json").read_text())
    s5 = json.loads(Path("outputs/step5/baselines/manifest.json").read_text())
    results = json.loads(Path("outputs/step6/features/results.json").read_text())
    features_config = json.loads(Path("configs/features.json").read_text())
    views = json.loads(Path("outputs/step4/repaired-views/manifest.json").read_text())
    identities = {}
    for relative, expected in audit["outputs"].items():
        path = Path("outputs/step2/repairs") / relative
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"upstream hash mismatch: {path}")
        identities[str(path)] = actual
    policy = Path("outputs/step2/repairs/model/training-model-table.parquet")
    policy_hash = identities[str(policy)]
    assert_identity({"policy": policy_hash, "response": s6["response_version"]}, {"policy": s5["inputs"]["training_model_table"], "response": s5["response_version"]})
    assert_identity({"policy": policy_hash, "claims": identities["outputs/step2/repairs/claims/matched.parquet"]}, {"policy": views["inputs"]["policy"], "claims": views["inputs"]["matched_claims"]})
    if policy_hash != s6["input_sha256"]:
        raise ValueError("Step 6 input identity mismatch")
    for path, expected in ((Path("configs/features.json"), s6["config_sha256"]), (Path("configs/baselines.json"), s5["inputs"]["config"]), (Path("src/iaa_hackathon/baselines.py"), s6["code_sha256"]["baselines.py"]), (Path("scripts/run_feature_experiments.py"), s6["code_sha256"]["run_feature_experiments.py"])):
        if sha256(path) != expected:
            raise ValueError(f"benchmark implementation/config changed: {path}")
    membership_path = Path("outputs/step4/folds/fold-membership.parquet")
    expected_digest = json.loads(Path("outputs/step4/folds/fold-summary.json").read_text())["membership_digest"]
    recovery = {"status": "not_needed"}
    try:
        member = pd.read_parquet(membership_path)
    except (OSError, ValueError) as exc:
        original_hash = sha256(membership_path)
        columns = ["row_id", "policy_id", "customer_id", "line", "period_start", "period_end", "exposure_clean"]
        member = build_membership(pd.read_parquet(policy, columns=columns), config)
        if membership_digest(member) != expected_digest:
            raise ValueError("reconstructed membership differs from original frozen logical digest")
        recovery_dir = args.output_dir / "fold-recovery"
        recovery_dir.mkdir(exist_ok=True)
        backup = recovery_dir / f"original-{original_hash}.parquet.corrupt"
        shutil.copy2(membership_path, backup)
        candidate = recovery_dir / "verified-replacement.parquet"
        member.to_parquet(candidate, index=False, compression="zstd")
        if membership_digest(pd.read_parquet(candidate)) != expected_digest or sha256(backup) != original_hash:
            raise ValueError("fold recovery verification failed; original preserved")
        candidate.replace(membership_path)
        recovery = {"status": "recovered_exact_original_membership", "original_error": str(exc), "original_sha256": original_hash, "backup": str(backup), "replacement_sha256": sha256(membership_path), "logical_digest": expected_digest}
        print(json.dumps(recovery), flush=True)
    if membership_digest(member) != expected_digest:
        raise ValueError("frozen fold membership digest mismatch")
    del member

    sources = set(sum(BASE_FEATURES.values(), []))
    for line, blocks in s6["selected_blocks"].items():
        for block in blocks:
            sources.update(features_config["blocks"][line][block]["source"])
    frame = pd.read_parquet(policy, columns=["row_id", "period_start", "line", "exposure_clean", "observed_net_incurred", *sorted(sources)])
    frame["period_year"] = pd.to_datetime(frame.period_start).dt.year
    reloads = []
    for fold_id, year in (("F2023", 2023), ("F2024", 2024)):
        valid = frame[frame.period_year.eq(year)]
        prediction_path = Path(f"outputs/step6/features/predictions/{fold_id}-selected.parquet")
        saved = align_predictions(valid, pd.read_parquet(prediction_path), fold=fold_id, response=s6["response_version"])
        reloaded = np.empty(len(valid))
        for line, blocks in s6["selected_blocks"].items():
            subset = valid[valid.line.eq(line)]
            derived, names = add_feature_blocks(subset, line, blocks)
            model = joblib.load(f"outputs/step6/features/models/{fold_id}-{line}-selected.joblib")
            reloaded[valid.line.eq(line).to_numpy()] = model.predict(derived[names]) * subset.exposure_clean.to_numpy(float)
        if not np.allclose(saved, reloaded, rtol=1e-12, atol=1e-10):
            raise ValueError(f"Step 6 saved-model reload mismatch: {fold_id}")
        measured = metric_report(valid.observed_net_incurred.to_numpy(float), saved)
        recorded = next(row for row in results if row["fold_id"] == fold_id and row["line"] == "pooled")
        if not np.isclose(measured["mean_tweedie_deviance"], recorded["mean_tweedie_deviance"], rtol=1e-12, atol=1e-12):
            raise ValueError(f"Step 6 recorded score mismatch: {fold_id}")
        identities[str(prediction_path)] = sha256(prediction_path)
        reloads.append({"fold_id": fold_id, "rows": len(valid), "reload_equivalent": True, **measured})
    report = {"status": "passed", "response_version": s6["response_version"], "claim_universe": views["claim_universe"], "experiment_mode": s6["experiment_mode"], "exposure": "exposure_clean; annual rate * exposure once", "fold_membership_digest": expected_digest, "fold_membership_sha256": sha256(membership_path), "fold_recovery": recovery, "inputs": identities, "benchmark_reload": reloads, "verified_at_ns": time.time_ns()}
    path = args.output_dir / "preflight.json"
    if path.exists():
        previous = json.loads(path.read_text())
        if recovery["status"] == "not_needed" and previous.get("fold_recovery", {}).get("status") == "recovered_exact_original_membership":
            report["fold_recovery"] = previous["fold_recovery"]
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "passed", "fold_digest": expected_digest, "S6_reload_rows": [item["rows"] for item in reloads]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
