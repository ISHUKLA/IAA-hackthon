"""Synthetic behavioral tests for submission validation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.submission import (
    SubmissionRules,
    SubmissionValidationError,
    order_like_sample,
    validate_submission_csv,
    validate_submission_frame,
)


FIXTURES = Path(__file__).parent / "fixtures" / "synthetic"
SAMPLE_IDS = ["M0001", "B0001", "C0001"]
OFFICIAL_RULES = SubmissionRules(expected_rows=3)
STRICT_RULES = SubmissionRules(expected_rows=3, strict_positive=True)


def valid_frame() -> pd.DataFrame:
    return pd.DataFrame({"row_id": SAMPLE_IDS, "prediction": [12.5, 4.25, 0.5]})


def test_valid_frame_and_csv_pass() -> None:
    assert validate_submission_frame(valid_frame(), SAMPLE_IDS, OFFICIAL_RULES)["status"] == "valid"
    result = validate_submission_csv(
        FIXTURES / "valid_submission.csv", SAMPLE_IDS, OFFICIAL_RULES
    )
    assert result["status"] == "valid"
    assert result["order_matches_sample"] is True


def test_reordered_ids_are_valid_but_reported_and_can_be_ordered() -> None:
    candidate = valid_frame().iloc[[2, 0, 1]].reset_index(drop=True)
    result = validate_submission_frame(candidate, SAMPLE_IDS, OFFICIAL_RULES)
    assert result["order_matches_sample"] is False
    ordered = order_like_sample(candidate, SAMPLE_IDS, OFFICIAL_RULES)
    assert ordered["row_id"].tolist() == SAMPLE_IDS


@pytest.mark.parametrize(
    ("candidate", "message"),
    [
        (pd.DataFrame({"row_id": SAMPLE_IDS[:2], "prediction": [1.0, 2.0]}), "row count"),
        (
            pd.DataFrame({"row_id": ["M0001", "B0001", "X0001"], "prediction": [1.0] * 3}),
            "1 missing, 1 extra",
        ),
        (
            pd.DataFrame({"row_id": ["M0001", "M0001", "C0001"], "prediction": [1.0] * 3}),
            "unique",
        ),
        (pd.DataFrame({"id": SAMPLE_IDS, "prediction": [1.0] * 3}), "columns"),
        (
            pd.DataFrame({"prediction": [1.0] * 3, "row_id": SAMPLE_IDS}),
            "columns",
        ),
        (
            pd.DataFrame({"row_id": SAMPLE_IDS, "prediction": [1.0] * 3, "index": [0, 1, 2]}),
            "columns",
        ),
        (
            pd.DataFrame({"row_id": [1, 2, 3], "prediction": [1.0] * 3}),
            "strings",
        ),
    ],
)
def test_identifier_and_structure_failures(candidate: pd.DataFrame, message: str) -> None:
    with pytest.raises(SubmissionValidationError, match=message):
        validate_submission_frame(candidate, SAMPLE_IDS, OFFICIAL_RULES)


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (["1", "2", "3"], "numeric"),
        ([True, False, True], "non-Boolean"),
        ([1.0, np.nan, 2.0], "finite"),
        ([1.0, np.inf, 2.0], "finite"),
        ([1.0, -0.01, 2.0], "at least 0"),
    ],
)
def test_invalid_prediction_values(values, message: str) -> None:
    candidate = pd.DataFrame({"row_id": SAMPLE_IDS, "prediction": values})
    with pytest.raises(SubmissionValidationError, match=message):
        validate_submission_frame(candidate, SAMPLE_IDS, OFFICIAL_RULES)


def test_zero_is_officially_valid_but_rejected_by_strict_local_policy() -> None:
    zeros = pd.DataFrame({"row_id": SAMPLE_IDS, "prediction": [0.0, 1.0, 2.0]})
    assert validate_submission_frame(zeros, SAMPLE_IDS, OFFICIAL_RULES)["status"] == "valid"
    with pytest.raises(SubmissionValidationError, match="strictly positive"):
        validate_submission_frame(zeros, SAMPLE_IDS, STRICT_RULES)


def test_csv_reread_rejects_accidental_index_column(tmp_path: Path) -> None:
    path = tmp_path / "with-index.csv"
    valid_frame().to_csv(path, index=True)
    with pytest.raises(SubmissionValidationError, match="columns"):
        validate_submission_csv(path, SAMPLE_IDS, OFFICIAL_RULES)


def test_csv_reread_preserves_leading_zero_ids_and_rejects_coercion(tmp_path: Path) -> None:
    correct = tmp_path / "correct.csv"
    correct.write_text("row_id,prediction\n001,1.0\n002,2.0\n003,3.0\n")
    assert validate_submission_csv(
        correct, ["001", "002", "003"], OFFICIAL_RULES
    )["status"] == "valid"

    coerced = tmp_path / "coerced.csv"
    coerced.write_text("row_id,prediction\n1,1.0\n2,2.0\n3,3.0\n")
    with pytest.raises(SubmissionValidationError, match="3 missing, 3 extra"):
        validate_submission_csv(coerced, ["001", "002", "003"], OFFICIAL_RULES)


def test_reference_sample_must_itself_be_unique_and_string_typed() -> None:
    with pytest.raises(ValueError, match="unique"):
        validate_submission_frame(valid_frame(), ["M0001", "M0001", "C0001"], OFFICIAL_RULES)
    with pytest.raises(ValueError, match="strings"):
        validate_submission_frame(valid_frame(), [1, 2, 3], OFFICIAL_RULES)


def test_nullable_numeric_missing_value_is_reported_as_nonfinite() -> None:
    candidate = pd.DataFrame(
        {
            "row_id": SAMPLE_IDS,
            "prediction": pd.Series([1.0, pd.NA, 2.0], dtype="Float64"),
        }
    )
    with pytest.raises(SubmissionValidationError, match="finite"):
        validate_submission_frame(candidate, SAMPLE_IDS, OFFICIAL_RULES)
