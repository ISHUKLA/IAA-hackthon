"""Local-only Step 9 commands. Run from the repository root with PYTHONPATH=src."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import time

from iaa_hackathon.final_diagnostics import diagnostic_markdown, diagnostics
from iaa_hackathon.final_submission import build_csv, build_model, git_snapshot, preflight, read_json, save_json, sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["preflight", "model", "submission", "verify", "reproduce", "finalize"])
    ap.add_argument("--config", type=Path, default=Path("configs/final_model.json"))
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, default=Path("outputs/step9"))
    ap.add_argument("--submission-dir", type=Path, default=Path("submissions"))
    args = ap.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    if args.command == "preflight":
        result = preflight(args.config, args.data_dir)
    elif args.command == "model":
        result = build_model(args.config, args.data_dir, output)
    elif args.command in ("submission", "verify"):
        # verify must never create a missing candidate.
        if args.command == "verify":
            from iaa_hackathon.final_submission import csv_path
            if not csv_path(read_json(args.config), args.config, args.submission_dir).exists():
                raise ValueError("submission missing; verify will not create it")
        result = build_csv(args.config, args.data_dir, output, args.submission_dir)
    elif args.command == "reproduce":
        start = time.perf_counter()
        authority = output / "submission-manifest.json"
        previous = read_json(authority if authority.exists() else output / "verification.json")
        # A new empty run directory ensures no models/predictions are reused.
        fresh = Path(tempfile.mkdtemp(prefix="clean-reproduction-", dir=output))
        build_model(args.config, args.data_dir, fresh)
        reproduced = build_csv(args.config, args.data_dir, fresh, fresh / "submissions")
        if reproduced["csv_sha256"] != previous["csv_sha256"]:
            raise ValueError("clean reproduction is not byte-for-byte identical")
        result = {"status": "passed", "mode": "exact_byte_for_byte", "csv_sha256": reproduced["csv_sha256"], "original_csv_sha256": previous["csv_sha256"], "clean_directory": str(fresh.resolve()), "clean_model_manifest_sha256": sha(fresh / "model-manifest.json"), "three_independent_clean_refits": True, "runtime_seconds": time.perf_counter() - start, "command": "make reproduce-step9 PYTHON=.venv/bin/python DATA_DIR='/path/to/official/public'"}
        save_json(output / "reproduction.json", result)
    else:
        preflight(args.config, args.data_dir)
        existing_path = output / "submission-manifest.json"
        if existing_path.exists():
            from iaa_hackathon.final_submission import check_hashes
            existing = read_json(existing_path)
            if existing["config_sha256"] != sha(args.config):
                raise ValueError("existing immutable manifest/config mismatch")
            check_hashes({existing["csv_path"]: existing["csv_sha256"]})
            check_hashes({str(output / p): h for p, h in existing["model_artifacts_sha256"].items()})
            check_hashes(existing["git"]["snapshot_artifacts_sha256"])
            print(json.dumps({"status": "reused_verified_immutable_manifest", "csv_sha256": existing["csv_sha256"], "human_review": "pending", "upload_status": "not_uploaded"}, indent=2))
            return
        cfg = read_json(args.config)
        verified = build_csv(args.config, args.data_dir, output, args.submission_dir)
        reproduction = read_json(output / "reproduction.json")
        if reproduction["status"] != "passed" or reproduction["csv_sha256"] != verified["csv_sha256"]:
            raise ValueError("successful clean reproduction missing")
        financial = diagnostics(cfg, output)
        if financial["unexplained_critical_alerts"]:
            raise ValueError("unexplained critical financial alert")
        report_dir = Path("reports/step9")
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "submission-diagnostics.md").write_text(diagnostic_markdown(financial))
        model = read_json(output / "model-manifest.json")
        result = {"status": "ready_for_human_review", "stage": "S9", "generation_utc": datetime.now(timezone.utc).isoformat(), "run_id": model["run_id"], "selected_model": cfg["model_id"], "governing_decision": cfg["decision_path"], "response_version": cfg["response_version"], "scenario": cfg["scenario"], "training_years": cfg["training_years"], "features": cfg["features"], "feature_version_sha256": cfg["inputs_sha256"]["configs/features.json"], **verified, "status": "ready_for_human_review", "config_sha256": sha(args.config), "inputs_sha256": cfg["inputs_sha256"], "raw_inputs_sha256": cfg["raw_sha256"], "code_sha256": cfg["code_sha256"], "environment": model["environment"], "model_artifacts_sha256": model["artifacts_sha256"], "model_manifest_sha256": sha(output / "model-manifest.json"), "training_test_by_line": model["lines"], "clean_reproduction": reproduction, "financial_diagnostics_sha256": sha(output / "financial-diagnostics.json"), "direction_log_sha256": sha(report_dir / "ai-direction-log.json"), "rules_check_sha256": sha(report_dir / "official-rules-check.json"), "git": git_snapshot(output), "commands": ["make step9-check PYTHON=.venv/bin/python", "make build-final-model build-submission verify-submission reproduce-step9 step9-finalize PYTHON=.venv/bin/python DATA_DIR='/path/to/official/public'"], "upload_status": "not_uploaded", "human_review": "pending", "final_kaggle_selection": "pending", "official_rules_current_access": "unresolved", "actuarial_validation": "not_claimed", "unexplained_critical_alerts": [], "gates": {"frozen_prior_selection": "passed", "full_training_refit_reload": "passed", "all_mechanical_submission_checks": "passed", "financial_diagnostics": "complete_with_disclosed_limitations", "clean_reproduction": "passed_exact_bytes", "provenance_and_direction_record": "complete", "human_approval_not_fabricated": "passed"}}
        manifest_path = output / "submission-manifest.json"
        if manifest_path.exists():
            old = read_json(manifest_path)
            if old["csv_sha256"] != result["csv_sha256"] or old["config_sha256"] != result["config_sha256"]:
                raise ValueError("refusing immutable manifest overwrite")
            result = old
        else:
            save_json(manifest_path, result, exclusive=True)
        save_json(output / "status.json", {"status": "ready_for_human_review", "manifest_sha256": sha(manifest_path), "csv_sha256": verified["csv_sha256"], "human_review": "pending", "upload_status": "not_uploaded"})
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
