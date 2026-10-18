"""One-command raw-data-free Step 2 schema and behavior verification."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    "configs/cleaning.json",
    "schemas/step2-clean-policy.schema.json",
    "schemas/step2-cleaning-ledger.schema.json",
    "src/iaa_hackathon/cleaning.py",
    "src/iaa_hackathon/prepare.py",
    "tests/test_cleaning.py",
    "tests/test_prepare.py",
    "docs/step2/cleaning-plan.md",
    "docs/step2/customer-identifiers.md",
    "docs/step2/exposure-reconciliation.md",
    "docs/step2/sum-insured-review.md",
    "docs/step2/missingness-and-availability.md",
    "docs/step2/join-reconciliation.md",
    "docs/step2/cleaning-report.md",
    "docs/step2/acceptance.md",
    "requirements/step2-py312.lock",
    "scripts/step2_acceptance.py",
)
TEST_PATHS = ("tests/test_cleaning.py", "tests/test_prepare.py")


def fail(message: str) -> int:
    print(json.dumps({"status": "failed", "error": message}, indent=2))
    return 1


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
    if missing:
        return fail(f"required Step 2 files are missing: {missing}")
    config = json.loads((ROOT / "configs/cleaning.json").read_text())
    if config["config_id"] != "step2-cleaning-v1":
        return fail("unexpected cleaning config identifier")
    for relative in (
        "schemas/step2-clean-policy.schema.json",
        "schemas/step2-cleaning-ledger.schema.json",
    ):
        Draft202012Validator.check_schema(json.loads((ROOT / relative).read_text()))
    collect = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *TEST_PATHS],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if collect.returncode != 0:
        print(collect.stdout, end="")
        print(collect.stderr, end="", file=sys.stderr)
        return fail("pytest collection failed")
    match = re.search(r"(\d+) tests? collected", collect.stdout)
    collected = int(match.group(1)) if match else 0
    if collected <= 0:
        return fail("pytest collected no Step 2 tests")
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *TEST_PATHS], cwd=ROOT, check=False
    )
    if run.returncode:
        return fail("Step 2 synthetic tests failed")
    print(json.dumps({
        "status": "passed",
        "schemas": "valid",
        "tests_collected": collected,
        "raw_data_required": False,
        "human_review": "pending",
        "scope": "Step 2 deterministic preparation only; no targets, models, or predictions.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
