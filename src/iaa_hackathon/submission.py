"""Submission-boundary validation without prediction generation or upload."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype


EXPECTED_COLUMNS = ("row_id", "prediction")
SAMPLE_ORDER_CONVENTION = "Generate and save rows in sample_submission order."


class SubmissionValidationError(ValueError):
    """Raised with all detected submission-contract failures."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass(frozen=True)
class SubmissionRules:
    expected_rows: int
    official_minimum: float = 0.0
    strict_positive: bool = False

    @classmethod
    def from_problem_contract(
        cls,
        path: str | Path = "configs/problem_contract.json",
    ) -> "SubmissionRules":
        contract = json.loads(Path(path).read_text())
        submission = contract["submission"]
        return cls(
            expected_rows=int(submission["row_count"]),
            official_minimum=float(submission["official_minimum"]),
        )


def _reference_ids(sample_ids: Iterable[object]) -> list[str]:
    values = list(sample_ids)
    if any(not isinstance(value, str) for value in values):
        raise ValueError("sample row_id values must be strings")
    if len(values) != len(set(values)):
        raise ValueError("sample row_id values must be unique")
    return values


def validate_submission_frame(
    candidate: pd.DataFrame,
    sample_ids: Iterable[object],
    rules: SubmissionRules,
) -> dict[str, object]:
    """Validate one candidate frame, collecting all applicable boundary errors."""
    errors: list[str] = []
    expected_ids = _reference_ids(sample_ids)
    expected_id_set = set(expected_ids)

    if list(candidate.columns) != list(EXPECTED_COLUMNS):
        errors.append("columns must be exactly ['row_id', 'prediction'] in that order")
    if len(candidate) != rules.expected_rows:
        errors.append(
            f"row count must be {rules.expected_rows}; received {len(candidate)}"
        )
    if len(expected_ids) != rules.expected_rows:
        errors.append(
            f"sample row count must be {rules.expected_rows}; received {len(expected_ids)}"
        )

    if "row_id" in candidate.columns:
        candidate_ids = candidate["row_id"].tolist()
        if any(not isinstance(value, str) for value in candidate_ids):
            errors.append("row_id values must be strings; identifier coercion is not allowed")
        else:
            candidate_id_set = set(candidate_ids)
            if len(candidate_ids) != len(candidate_id_set):
                errors.append("row_id values must be unique")
            missing_count = len(expected_id_set - candidate_id_set)
            extra_count = len(candidate_id_set - expected_id_set)
            if missing_count or extra_count:
                errors.append(
                    "row_id coverage must exactly match sample IDs "
                    f"({missing_count} missing, {extra_count} extra)"
                )

    if "prediction" in candidate.columns:
        predictions = candidate["prediction"]
        if not is_numeric_dtype(predictions.dtype) or is_bool_dtype(predictions.dtype):
            errors.append("prediction must have a numeric, non-Boolean dtype")
        else:
            numeric = predictions.to_numpy(dtype=float, na_value=np.nan)
            if not np.isfinite(numeric).all():
                errors.append("prediction values must all be finite")
            if np.any(numeric < rules.official_minimum):
                errors.append(
                    f"prediction values must be at least {rules.official_minimum:g}"
                )
            if rules.strict_positive and np.any(numeric <= 0):
                errors.append(
                    "prediction values must be strictly positive under the local Tweedie policy"
                )

    if errors:
        raise SubmissionValidationError(errors)
    return {
        "status": "valid",
        "rows": len(candidate),
        "columns": list(candidate.columns),
        "exact_id_coverage": True,
        "order_matches_sample": candidate["row_id"].tolist() == expected_ids,
        "official_minimum": rules.official_minimum,
        "strict_positive": rules.strict_positive,
    }


def validate_submission_csv(
    candidate_path: str | Path,
    sample_ids: Iterable[object],
    rules: SubmissionRules,
) -> dict[str, object]:
    """Reread and validate a CSV while preserving identifier text exactly."""
    try:
        candidate = pd.read_csv(
            candidate_path,
            dtype={"row_id": "string"},
            keep_default_na=True,
        )
    except (OSError, pd.errors.ParserError, UnicodeError) as exc:
        raise SubmissionValidationError([f"candidate CSV could not be read: {exc}"]) from exc
    if "row_id" in candidate.columns:
        candidate["row_id"] = candidate["row_id"].astype(object)
    return validate_submission_frame(candidate, sample_ids, rules)


def order_like_sample(
    candidate: pd.DataFrame,
    sample_ids: Iterable[object],
    rules: SubmissionRules,
) -> pd.DataFrame:
    """Return a validated candidate in the deterministic sample-order convention."""
    expected_ids = _reference_ids(sample_ids)
    validate_submission_frame(candidate, expected_ids, rules)
    indexed = candidate.set_index("row_id", verify_integrity=True)
    ordered = indexed.loc[expected_ids].reset_index()
    return ordered.loc[:, list(EXPECTED_COLUMNS)]
