"""Synthetic and structural tests for the machine-readable problem contract."""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "configs/problem_contract.json").read_text())
SCHEMA = json.loads((ROOT / "schemas/problem_contract.schema.json").read_text())


def test_schema_and_contract_validate() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    Draft202012Validator(SCHEMA).validate(CONTRACT)


def test_human_review_remains_pending_and_unknowns_remain_null() -> None:
    assert CONTRACT["approval"]["human_actuarial_review"] == "pending"
    assert CONTRACT["metric"]["pooling"]["value"] is None
    assert CONTRACT["metric"]["sample_weighting"]["value"] is None
    assert CONTRACT["submission"]["order_required_officially"] is None
    assert CONTRACT["target"]["financial_field_interpretation"]["value"] is None


def test_loss_date_example_uses_inclusive_coverage_not_report_date() -> None:
    start = date(2025, 1, 1)
    end = date(2025, 6, 30)
    assert start <= date(2025, 5, 15) <= end
    assert not start <= date(2025, 7, 1) <= end
    assert CONTRACT["claim_allocation"]["date_field"] == "loss_date"
    assert CONTRACT["claim_allocation"]["boundaries"] == "inclusive"


def test_expectation_exposure_and_aggregation_examples() -> None:
    examples = CONTRACT["examples"]
    expectation = examples["expectation"]
    assert expectation["claim_probability"] * expectation["conditional_cost"] == 100.0
    exposure = examples["exposure"]
    assert exposure["annual_expected_cost"] * exposure["exposure"] == 50.0
    aggregation = examples["aggregation"]
    assert aggregation["policy_count"] * aggregation["per_policy_expected_cost"] == 50000.0


def test_d2_example() -> None:
    example = CONTRACT["examples"]["d2"]
    calculated = 1 - example["model_deviance"] / example["null_deviance"]
    assert math.isclose(calculated, example["score"])


def test_submission_contract_keeps_official_and_local_zero_rules_separate() -> None:
    submission = CONTRACT["submission"]
    assert submission["columns"] == ["row_id", "prediction"]
    assert submission["row_count"] == 626639
    assert submission["official_minimum"] == 0.0
    assert submission["strict_positive_local_tweedie_compatibility"] is True
