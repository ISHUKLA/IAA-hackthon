"""Raw-data-free Step 3 schema, configuration and behavioral gate."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
TESTS = ("tests/test_claim_targets.py", "tests/test_reporting.py")
REQUIRED = (
    "configs/target_construction.json", "configs/reserving_scenarios.json",
    "schemas/step3-claim-linkage.schema.json", "schemas/step3-target-row.schema.json",
    "src/iaa_hackathon/claim_targets.py", "src/iaa_hackathon/reporting.py",
    "src/iaa_hackathon/targets_pipeline.py", "requirements/step3-py312.lock",
    "scripts/step3_acceptance.py", *TESTS,
)


def fail(message: str) -> int:
    print(json.dumps({"status": "failed", "error": message}, indent=2))
    return 1


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    if missing:
        return fail(f"required Step 3 files are missing: {missing}")
    target = json.loads((ROOT / "configs/target_construction.json").read_text())
    scenario = json.loads((ROOT / "configs/reserving_scenarios.json").read_text())
    if target["scope"]["test_target_construction"] or target["scope"]["pricing_model_training"]:
        return fail("Step 3 config exceeds permitted scope")
    if scenario["trend_to_2025_cost_level"]["enabled"]:
        return fail("trend must remain disabled in Step 3")
    for relative in ("schemas/step3-claim-linkage.schema.json", "schemas/step3-target-row.schema.json"):
        Draft202012Validator.check_schema(json.loads((ROOT / relative).read_text()))
    collect = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *TESTS],
        cwd=ROOT, text=True, capture_output=True,
    )
    match = re.search(r"(\d+) tests? collected", collect.stdout)
    count = int(match.group(1)) if match else 0
    if collect.returncode or count <= 0:
        return fail("Step 3 pytest collection failed or collected zero tests")
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", *TESTS], cwd=ROOT)
    if run.returncode:
        return fail("Step 3 synthetic tests failed")
    print(json.dumps({
        "status": "passed", "tests_collected": count, "schemas": "valid",
        "raw_data_required": False, "human_review": "pending",
        "scope": "linkage, observed accounting, delay estimator and scenario behavior; no pricing models",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
