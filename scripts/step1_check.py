"""One-command, raw-data-free Step 1 contract verification."""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    "configs/problem_contract.json",
    "schemas/problem_contract.schema.json",
    "docs/step1/problem-definition.md",
    "docs/step1/data-readiness.md",
    "docs/step1/submission-validation.md",
    "docs/step1/challenge-review.md",
    "docs/step1/acceptance.md",
    "docs/assumptions.md",
    "src/iaa_hackathon/metrics.py",
    "src/iaa_hackathon/submission.py",
    "tests/test_contract.py",
    "tests/test_metrics.py",
    "tests/test_submission.py",
    "requirements/step1-py312.lock",
)
TEST_PATHS = (
    "tests/test_contract.py",
    "tests/test_metrics.py",
    "tests/test_submission.py",
)


def _fail(message: str) -> int:
    print(json.dumps({"status": "failed", "error": message}, indent=2))
    return 1


def main() -> int:
    missing = [relative for relative in REQUIRED_PATHS if not (ROOT / relative).is_file()]
    if missing:
        return _fail(f"required Step 1 files are missing: {missing}")

    schema = json.loads((ROOT / "schemas/problem_contract.schema.json").read_text())
    contract = json.loads((ROOT / "configs/problem_contract.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)

    examples = contract["examples"]
    if examples["expectation"]["claim_probability"] * examples["expectation"]["conditional_cost"] != 100:
        return _fail("expectation example failed")
    if examples["exposure"]["annual_expected_cost"] * examples["exposure"]["exposure"] != 50:
        return _fail("exposure example failed")
    if examples["aggregation"]["policy_count"] * examples["aggregation"]["per_policy_expected_cost"] != 50000:
        return _fail("aggregation example failed")
    d2 = 1 - examples["d2"]["model_deviance"] / examples["d2"]["null_deviance"]
    if not math.isclose(d2, examples["d2"]["score"]):
        return _fail("D² example failed")

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
        return _fail("pytest collection failed")
    match = re.search(r"(\d+) tests? collected", collect.stdout)
    collected = int(match.group(1)) if match else 0
    if collected <= 0:
        return _fail("pytest collected no Step 1 tests")

    tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *TEST_PATHS],
        cwd=ROOT,
        check=False,
    )
    if tests.returncode != 0:
        return _fail("Step 1 behavioral tests failed")

    print(json.dumps({
        "status": "passed",
        "contract_schema": "valid",
        "synthetic_examples": "passed",
        "tests_collected": collected,
        "raw_data_required": False,
        "human_actuarial_review": contract["approval"]["human_actuarial_review"],
        "scope": "Step 1 contract verification only; no model or prediction validation.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
