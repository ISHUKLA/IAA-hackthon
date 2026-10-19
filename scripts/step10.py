"""Local-only Step 10 orchestration; failed gates never alter the candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import time

from iaa_hackathon.final_submission import save_json, sha
from iaa_hackathon.part1_handoff import accept_handoff, aggregate_review, build_handoff, freeze_candidate, reproduce_candidate, verify_candidate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["freeze", "check", "verify", "reproduce", "review", "package", "acceptance"])
    ap.add_argument("--data-dir", type=Path)
    ap.add_argument("--output-dir", type=Path, default=Path("outputs/step10"))
    args = ap.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    try:
        if args.command == "check":
            command = [sys.executable, "-m", "pytest", "-q", "tests/test_part1_handoff.py", "tests/test_final_submission.py", "tests/test_baselines.py", "tests/test_metrics.py", "tests/test_submission.py", "tests/test_reporting.py", "tests/test_validation_folds.py", "tests/test_validation_scoring.py"]
            run = subprocess.run(command, text=True, capture_output=True)
            print(run.stdout)
            count = re.search(r"(\d+) passed", run.stdout)
            if run.returncode or count is None or int(count.group(1)) == 0:
                raise ValueError("nonzero passing Step 10 suite required")
            result = {"status": "passed", "passed_tests": int(count.group(1)), "runtime_seconds": time.perf_counter() - start, "command": "make step10-check PYTHON=.venv/bin/python", "code_sha256": {p: sha(Path(p)) for p in ("src/iaa_hackathon/part1_handoff.py", "scripts/step10.py", "tests/test_part1_handoff.py")}, "pytest_summary": run.stdout.splitlines()[-1]}
            save_json(output / "tests.json", result)
        elif args.command == "freeze":
            frozen = freeze_candidate(output)
            result = {"status": "passed", "candidate_sha256": frozen["submission"]["sha256"]}
        elif args.command in {"verify", "reproduce", "review"}:
            if args.data_dir is None or not args.data_dir.is_dir():
                raise ValueError("provide the existing official public-data directory")
            fn = {"verify": verify_candidate, "reproduce": reproduce_candidate, "review": aggregate_review}[args.command]
            result = fn(output, args.data_dir)
            if args.command == "review":
                result = {"status": result["status"], "region_groups": len(result["region_calibration"]), "peril_year_groups": len(result["peril_maturity"]), "artifact": str(output / "aggregate-review.json"), "predictions_changed": False}
        elif args.command == "package":
            result = build_handoff(output)
        else:
            result = accept_handoff(output)
    except Exception as exc:
        save_json(output / "last-failure.json", {"status": "failed_verification", "command": args.command, "error_type": type(exc).__name__, "error": str(exc).replace(str(Path.cwd()), "<repository>")})
        save_json(output / "status.json", {"status": "failed_verification", "failed_command": args.command, "upload_status": "not_uploaded", "human_review": "pending", "part2_execution": "not_started"})
        raise
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
