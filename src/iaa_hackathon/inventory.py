"""Read-only inventory of the local competition Parquet inputs."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow
import pyarrow.compute as pc
import pyarrow.parquet as pq


TRAIN_FILES = (
    "policies_buildings.parquet",
    "policies_contents.parquet",
    "policies_motor.parquet",
)
TEST_FILES = (
    "test_buildings.parquet",
    "test_contents.parquet",
    "test_motor.parquet",
)
POLICY_COLUMNS = ("row_id", "policy_id", "period_start", "period_end", "exposure")
CLAIM_COLUMNS = (
    "claim_id",
    "policy_id",
    "loss_date",
    "report_date",
    "status",
    "incurred_to_date",
    "recoveries",
)
SAMPLE_COLUMNS = ("row_id", "prediction")


def _json_value(value: Any) -> Any:
    if hasattr(value, "as_py"):
        value = value.as_py()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stat(path: Path) -> dict[str, int]:
    value = path.stat()
    return {
        "size_bytes": value.st_size,
        "mtime_ns": value.st_mtime_ns,
        "inode": value.st_ino,
    }


def _min_max(column: pyarrow.ChunkedArray) -> dict[str, Any]:
    result = pc.min_max(column)
    return {
        "min": _json_value(result["min"]),
        "max": _json_value(result["max"]),
    }


def _column_summary(column: pyarrow.ChunkedArray) -> dict[str, Any]:
    return {
        "type": str(column.type),
        "null_count": column.null_count,
        **_min_max(column),
    }


def _read_required(path: Path, required: tuple[str, ...]) -> pyarrow.Table:
    schema_names = pq.ParquetFile(path).schema_arrow.names
    missing = [name for name in required if name not in schema_names]
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {missing}")
    return pq.read_table(path, columns=list(required))


def _policy_summary(path: Path) -> tuple[dict[str, Any], set[str]]:
    table = _read_required(path, POLICY_COLUMNS)
    row_ids = table["row_id"]
    row_id_values = row_ids.to_pylist()
    row_id_set = set(row_id_values)
    summary = {
        "rows_inspected": table.num_rows,
        "required_columns": list(POLICY_COLUMNS),
        "row_id": {
            "type": str(row_ids.type),
            "null_count": row_ids.null_count,
            "distinct_count": len(row_id_set),
            "unique_and_non_null": row_ids.null_count == 0 and len(row_id_set) == table.num_rows,
        },
        "policy_id": {
            "type": str(table["policy_id"].type),
            "null_count": table["policy_id"].null_count,
            "distinct_count": int(pc.count_distinct(table["policy_id"]).as_py()),
        },
        "period_start": _column_summary(table["period_start"]),
        "period_end": _column_summary(table["period_end"]),
        "exposure": _column_summary(table["exposure"]),
    }
    return summary, row_id_set


def _claims_summary(path: Path) -> dict[str, Any]:
    table = _read_required(path, CLAIM_COLUMNS)
    statuses = sorted(
        value for value in pc.unique(table["status"]).to_pylist() if value is not None
    )
    return {
        "rows_inspected": table.num_rows,
        "required_columns": list(CLAIM_COLUMNS),
        "claim_id": {
            "type": str(table["claim_id"].type),
            "null_count": table["claim_id"].null_count,
            "distinct_count": int(pc.count_distinct(table["claim_id"]).as_py()),
        },
        "policy_id": {
            "type": str(table["policy_id"].type),
            "null_count": table["policy_id"].null_count,
            "distinct_count": int(pc.count_distinct(table["policy_id"]).as_py()),
        },
        "loss_date": _column_summary(table["loss_date"]),
        "report_date": _column_summary(table["report_date"]),
        "status": {
            "type": str(table["status"].type),
            "null_count": table["status"].null_count,
            "values": statuses,
        },
        "incurred_to_date": _column_summary(table["incurred_to_date"]),
        "recoveries": _column_summary(table["recoveries"]),
    }


def _sample_summary(path: Path, test_ids: set[str]) -> dict[str, Any]:
    parquet = pq.ParquetFile(path)
    table = _read_required(path, SAMPLE_COLUMNS)
    sample_ids_list = table["row_id"].to_pylist()
    sample_ids = set(sample_ids_list)
    predictions = table["prediction"]
    exact_columns = parquet.schema_arrow.names == list(SAMPLE_COLUMNS)
    all_zero = bool(pc.all(pc.fill_null(pc.equal(predictions, 0), False)).as_py())
    return {
        "rows_inspected": table.num_rows,
        "columns": parquet.schema_arrow.names,
        "columns_exact": exact_columns,
        "row_id_null_count": table["row_id"].null_count,
        "row_id_distinct_count": len(sample_ids),
        "row_id_unique_and_non_null": (
            table["row_id"].null_count == 0 and len(sample_ids) == table.num_rows
        ),
        "test_keys_missing_from_sample": len(test_ids - sample_ids),
        "sample_keys_not_in_test": len(sample_ids - test_ids),
        "exact_test_key_coverage": sample_ids == test_ids,
        "prediction": {
            **_column_summary(predictions),
            "all_zero": all_zero,
            "interpretation": "All-zero placeholders; these are not labels." if all_zero else (
                "Submission template values are not treated as labels."
            ),
        },
    }


def build_inventory(
    data_dir: Path,
    config_path: Path,
    manifest_path: Path,
) -> tuple[dict[str, Any], bool]:
    """Inspect inputs without writing to the data directory."""
    config = json.loads(config_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    expected = {item["filename"]: item for item in manifest["files"]}
    names = config["expected_files"]
    root = data_dir.expanduser().resolve()
    missing = [name for name in names if not (root / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing expected inputs: {missing}")

    pre_stats = {name: _stat(root / name) for name in names}
    files: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    for name in names:
        path = root / name
        parquet = pq.ParquetFile(path)
        hashes[name] = _sha256(path)
        actual = {
            "filename": name,
            "rows": parquet.metadata.num_rows,
            "columns": parquet.metadata.num_columns,
            "sha256": hashes[name],
            "schema": [
                {"name": field.name, "type": str(field.type), "nullable": field.nullable}
                for field in parquet.schema_arrow
            ],
        }
        reference = expected.get(name)
        actual["reference_match"] = {
            "rows": reference is not None and actual["rows"] == reference["rows"],
            "columns": reference is not None and actual["columns"] == reference["columns"],
            "sha256": reference is not None and actual["sha256"] == reference["sha256"],
            "all": reference is not None and all(
                (
                    actual["rows"] == reference["rows"],
                    actual["columns"] == reference["columns"],
                    actual["sha256"] == reference["sha256"],
                )
            ),
        }
        files.append(actual)

    policy: dict[str, dict[str, Any]] = {}
    test_id_sets: list[set[str]] = []
    for name in (*TRAIN_FILES, *TEST_FILES):
        summary, row_ids = _policy_summary(root / name)
        policy[name] = summary
        if name in TEST_FILES:
            test_id_sets.append(row_ids)

    all_test_ids: set[str] = set()
    test_id_rows = 0
    for values, name in zip(test_id_sets, TEST_FILES, strict=True):
        all_test_ids.update(values)
        test_id_rows += policy[name]["rows_inspected"]

    claims = _claims_summary(root / "claims.parquet")
    sample = _sample_summary(root / "sample_submission.parquet", all_test_ids)
    post_stats = {name: _stat(root / name) for name in names}
    stats_unchanged = all(pre_stats[name] == post_stats[name] for name in names)
    manifest_matches = all(item["reference_match"]["all"] for item in files)
    policy_keys_valid = all(item["row_id"]["unique_and_non_null"] for item in policy.values())
    test_keys_unique = len(all_test_ids) == test_id_rows and all(
        policy[name]["row_id"]["unique_and_non_null"] for name in TEST_FILES
    )
    expected_test_rows = config["expected_test_rows"]
    training_dates_in_expected_range = all(
        "2021-01-01" <= policy[name][column]["min"]
        and policy[name][column]["max"] <= "2024-12-31"
        for name in TRAIN_FILES
        for column in ("period_start", "period_end")
    )
    test_dates_in_expected_range = all(
        "2025-01-01" <= policy[name][column]["min"]
        and policy[name][column]["max"] <= "2025-12-31"
        for name in TEST_FILES
        for column in ("period_start", "period_end")
    )
    acceptance = {
        "all_11_files_match_reference_manifest": manifest_matches and len(files) == 11,
        "all_policy_row_keys_unique_and_non_null": policy_keys_valid,
        "training_policy_dates_within_2021_2024": training_dates_in_expected_range,
        "test_policy_dates_within_2025": test_dates_in_expected_range,
        "combined_test_row_ids_unique_and_non_null": test_keys_unique,
        "combined_test_rows": test_id_rows,
        "combined_test_rows_match_expected": test_id_rows == expected_test_rows,
        "combined_test_distinct_row_ids": len(all_test_ids),
        "sample_rows_match_expected": sample["rows_inspected"] == expected_test_rows,
        "sample_columns_are_exact": sample["columns_exact"],
        "sample_row_ids_unique_and_non_null": sample["row_id_unique_and_non_null"],
        "sample_has_exact_test_key_coverage": sample["exact_test_key_coverage"],
        "sample_predictions_are_all_zero_placeholders": sample["prediction"]["all_zero"],
        "raw_file_stats_unchanged_after_inspection": stats_unchanged,
        "raw_hash_continuity_verified": manifest_matches and stats_unchanged,
    }
    passed = all(
        value for key, value in acceptance.items()
        if key not in {"combined_test_rows", "combined_test_distinct_row_ids"}
    )
    inventory = {
        "schema_version": 1,
        "status": "ready" if passed else "discrepancy",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Read-only metadata, hashes, required columns and key coverage; no repairs or labels constructed.",
        "data_dir": str(root),
        "runtime": {
            "python": platform.python_version(),
            "implementation": sys.implementation.name,
            "pyarrow": pyarrow.__version__,
        },
        "reference_manifest": str(manifest_path.resolve()),
        "hash_method": (
            "Each file was hashed once and that digest was reused for all comparisons. "
            "Pre/post size, mtime and inode checks establish that inputs were not changed during inspection."
        ),
        "files": files,
        "policy_required_columns": policy,
        "claims_required_columns": claims,
        "sample_submission": sample,
        "pre_post_stat_match": {
            name: pre_stats[name] == post_stats[name] for name in names
        },
        "acceptance": acceptance,
    }
    return inventory, passed


def write_inventory(inventory: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    temporary.replace(output_path)
