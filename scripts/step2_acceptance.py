"""Validate the real-data Step 2 reconciliation without reading raw records."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/step2/prepared")
    parser.add_argument("--config", default="configs/cleaning.json")
    args = parser.parse_args()
    output = Path(args.output_dir)
    config = json.loads(Path(args.config).read_text())
    manifest = json.loads((output / config["outputs"]["manifest"]).read_text())
    reconciliation = json.loads((output / config["outputs"]["reconciliation"]).read_text())
    expected = config["regression_reference"]
    errors: list[str] = []

    if manifest["status"] != "complete" or not manifest["raw_hashes_unchanged"]:
        errors.append("manifest is incomplete or raw hashes changed")
    if manifest.get("rerun_comparison", {}).get("matches_previous_run") is not True:
        errors.append("a matching repeated-run logical digest is not recorded")
    for name, rows in expected["policy_rows"].items():
        actual = reconciliation["files"][name]
        if actual["rows_before"] != rows or actual["rows_after"] != rows:
            errors.append(f"{name}: row count differs from reference")
        if not actual["row_id_exact_order_preserved"] or not actual["row_id_unique_and_non_null"]:
            errors.append(f"{name}: row identity failed")
        if not actual["original_columns_preserved"]:
            errors.append(f"{name}: source column changed")
        if actual["written_premium_total_before"] != actual["written_premium_total_after"]:
            errors.append(f"{name}: written premium total changed")
        for dimension in ("customer", "address", "weather"):
            if actual[f"{dimension}_join_status"] != {"matched": rows}:
                errors.append(f"{name}: {dimension} linkage is incomplete")
    for name, count in expected["customer_id_changed_rows"].items():
        if reconciliation["files"][name]["customer_id_changed_rows"] != count:
            errors.append(f"{name}: customer repair count differs from reference")
    exposure_changed = sum(
        reconciliation["files"][name]["exposure_changed_rows"]
        for name in ("policies_motor.parquet", "policies_buildings.parquet", "policies_contents.parquet")
    )
    if exposure_changed != expected["training_exposure_exception_rows"]:
        errors.append("training exposure exception count differs from reference")
    for name in ("test_motor.parquet", "test_buildings.parquet", "test_contents.parquet"):
        file_result = reconciliation["files"][name]
        if file_result["exposure_changed_rows"] != 0 or file_result["exposure_raw_total"] != file_result["exposure_clean_total"]:
            errors.append(f"{name}: test exposure changed")
    for name, count in expected["sum_insured_candidate_rows"].items():
        if reconciliation["files"][name]["sum_insured_candidate_rows"] != count:
            errors.append(f"{name}: sum-insured candidate count differs from reference")
    tracked = set(
        subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
    )
    prohibited = [item for item in tracked if item.startswith("outputs/step2/")]
    if prohibited:
        errors.append(f"Step 2 row-level output is tracked: {prohibited}")
    if errors:
        print(json.dumps({"status": "failed", "errors": errors}, indent=2))
        return 1
    print(json.dumps({
        "status": "passed",
        "policy_rows": sum(expected["policy_rows"].values()),
        "customer_id_repairs": sum(expected["customer_id_changed_rows"].values()),
        "training_exposure_corrections": exposure_changed,
        "sum_insured_candidates": sum(expected["sum_insured_candidate_rows"].values()),
        "ledger_rows": reconciliation["ledger_rows"],
        "logical_output_digest": manifest["logical_output_digest"],
        "raw_hashes_unchanged": True,
        "human_sum_insured_adoption": "pending",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

