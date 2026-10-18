"""Reproducible, source-preserving Step 2 policy preparation pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow

from iaa_hackathon.cleaning import (
    DataQualityError,
    derive_exposure,
    derive_sum_insured_candidate,
    motor_quality_flags,
    normalize_customer_ids,
    validate_unique_dimension,
)


POLICY_METADATA = {
    "policies_motor.parquet": ("motor", "train"),
    "test_motor.parquet": ("motor", "test"),
    "policies_buildings.parquet": ("buildings", "train"),
    "test_buildings.parquet": ("buildings", "test"),
    "policies_contents.parquet": ("contents", "train"),
    "test_contents.parquet": ("contents", "test"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_scalar(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    return json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))


def _input_hashes(data_dir: Path, manifest: dict[str, Any]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for item in manifest["files"]:
        path = data_dir / item["filename"]
        if not path.is_file():
            raise DataQualityError(f"missing expected input: {item['filename']}")
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise DataQualityError(f"source hash mismatch: {item['filename']}")
        hashes[item["filename"]] = actual
    return hashes


def _code_digest(root: Path, cleaning_config: Path) -> tuple[str, list[str]]:
    relative = [
        "src/iaa_hackathon/cleaning.py",
        "src/iaa_hackathon/prepare.py",
        "src/iaa_hackathon/__main__.py",
        "schemas/step2-clean-policy.schema.json",
        "schemas/step2-cleaning-ledger.schema.json",
    ]
    paths = [root / item for item in relative] + [cleaning_config]
    digest = hashlib.sha256()
    labels: list[str] = []
    for path in paths:
        label = str(path.relative_to(root)) if path.is_relative_to(root) else path.name
        labels.append(label)
        digest.update(label.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest(), labels


def _membership_status(values: pd.Series, reference: pd.Index) -> pd.Series:
    status = pd.Series("unresolved_reference", index=values.index, dtype="string")
    status.loc[values.isna()] = "missing_key"
    status.loc[values.notna() & values.isin(reference)] = "matched"
    return status


def _append_ledger(
    ledgers: list[pd.DataFrame],
    frame: pd.DataFrame,
    mask: pd.Series,
    *,
    source_file: str,
    field: str,
    original: pd.Series,
    derived: pd.Series,
    rule_id: str,
    rule_version: int,
    reason: pd.Series,
    evidence_status: str,
    change_status: str,
) -> None:
    selected = frame.loc[mask, ["row_id"]].copy()
    if selected.empty:
        return
    selected["source_file"] = source_file
    selected["entity_key"] = selected["row_id"]
    selected["field"] = field
    selected["original_value"] = original.loc[mask].map(_json_scalar)
    selected["derived_value"] = derived.loc[mask].map(_json_scalar)
    selected["rule_id"] = rule_id
    selected["rule_version"] = rule_version
    selected["reason"] = reason.loc[mask].astype(str)
    selected["evidence_status"] = evidence_status
    selected["change_status"] = change_status
    ledgers.append(
        selected[
            [
                "source_file",
                "row_id",
                "entity_key",
                "field",
                "original_value",
                "derived_value",
                "rule_id",
                "rule_version",
                "reason",
                "evidence_status",
                "change_status",
            ]
        ]
    )


def _missingness_by_year(frame: pd.DataFrame, years: pd.Series) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for year in sorted(years.unique()):
        subset = frame.loc[years.eq(year)]
        result[str(int(year))] = {
            column: int(count)
            for column, count in subset.isna().sum().items()
            if int(count) > 0
        }
    return result


def _clean_policy(
    source: pd.DataFrame,
    *,
    source_file: str,
    line: str,
    split: str,
    config: dict[str, Any],
    customer_ids: pd.Index,
    address_ids: pd.Index,
    weather_keys: pd.MultiIndex,
) -> tuple[pd.DataFrame, list[pd.DataFrame], dict[str, Any]]:
    frame = source.copy()
    original_columns = list(source.columns)
    if frame["row_id"].isna().any() or not frame["row_id"].is_unique:
        raise DataQualityError(f"{source_file}: row_id must be unique and non-null")
    original_ids = frame["row_id"].tolist()
    original_premium_total = float(frame["written_premium"].sum())

    identifiers = normalize_customer_ids(frame["customer_id"], customer_ids, width=8)
    exposure = derive_exposure(
        frame["period_start"],
        frame["period_end"],
        frame["exposure"],
        decimals=4,
        absolute_tolerance=0.00005,
        strict=True,
    )
    frame = pd.concat([frame, identifiers, exposure], axis=1)
    frame["source_file"] = source_file
    frame["line"] = line
    frame["split"] = split
    frame["cleaning_config_version"] = config["config_id"]

    if line in {"buildings", "contents"}:
        parameters = next(
            rule["parameters"]
            for rule in config["rules"]
            if rule["rule_id"] == "sum_insured_unit_candidate"
        )
        candidate = derive_sum_insured_candidate(
            frame["sum_insured"],
            line=line,
            separator=float(parameters["diagnostic_separators"][line]),
            divisor=float(parameters["proposed_divisor"]),
        )
        frame = pd.concat([frame, candidate], axis=1)
    else:
        frame["sum_insured_raw"] = pd.Series(pd.NA, index=frame.index, dtype="Float64")
        frame["sum_insured_candidate"] = pd.Series(pd.NA, index=frame.index, dtype="Float64")
        frame["sum_insured_unit_error_flag"] = pd.Series(pd.NA, index=frame.index, dtype="boolean")
        frame["sum_insured_proposed_divisor"] = pd.Series(pd.NA, index=frame.index, dtype="Float64")
        frame["sum_insured_candidate_reason"] = "not_applicable_to_motor"
        frame["sum_insured_candidate_status"] = "not_applicable"

    if line == "motor":
        frame = pd.concat([frame, motor_quality_flags(frame)], axis=1)

    frame["customer_join_status"] = _membership_status(frame["customer_id_clean"], customer_ids)
    frame["address_join_status"] = _membership_status(frame["address_id"], address_ids)
    start = pd.to_datetime(frame["period_start"])
    end = pd.to_datetime(frame["period_end"])
    cross_year = start.dt.year.ne(end.dt.year)
    policy_weather = pd.MultiIndex.from_arrays([frame["address_id"], start.dt.year])
    weather_match = pd.Series(policy_weather.isin(weather_keys), index=frame.index)
    weather_status = pd.Series("unresolved_reference", index=frame.index, dtype="string")
    weather_status.loc[frame["address_id"].isna()] = "missing_key"
    weather_status.loc[~cross_year & weather_match] = "matched"
    weather_status.loc[cross_year] = "cross_year_period"
    frame["weather_join_status"] = weather_status
    frame["weather_year"] = start.dt.year.astype("Int64").where(~cross_year)

    unresolved_customer = frame["customer_join_status"].ne("matched")
    unresolved_address = frame["address_join_status"].ne("matched")
    unresolved_weather = frame["weather_join_status"].ne("matched")
    if unresolved_customer.any() or unresolved_address.any() or unresolved_weather.any():
        raise DataQualityError(
            f"{source_file}: unresolved joins customer={int(unresolved_customer.sum())}, "
            f"address={int(unresolved_address.sum())}, weather={int(unresolved_weather.sum())}"
        )

    ledgers: list[pd.DataFrame] = []
    _append_ledger(
        ledgers,
        frame,
        frame["customer_id_changed"],
        source_file=source_file,
        field="customer_id",
        original=frame["customer_id_raw"],
        derived=frame["customer_id_clean"],
        rule_id="customer_id_normalization",
        rule_version=1,
        reason=frame["customer_id_reason"],
        evidence_status="verified",
        change_status="changed",
    )
    _append_ledger(
        ledgers,
        frame,
        frame["exposure_changed"],
        source_file=source_file,
        field="exposure",
        original=frame["exposure_raw"],
        derived=frame["exposure_clean"],
        rule_id="inclusive_act365_exposure",
        rule_version=1,
        reason=frame["exposure_reason"],
        evidence_status="verified",
        change_status="changed",
    )
    if line in {"buildings", "contents"}:
        inferred = frame["sum_insured_candidate_status"].eq("inferred")
        _append_ledger(
            ledgers,
            frame,
            inferred,
            source_file=source_file,
            field="sum_insured",
            original=frame["sum_insured_raw"],
            derived=frame["sum_insured_candidate"],
            rule_id="sum_insured_unit_candidate",
            rule_version=1,
            reason=frame["sum_insured_candidate_reason"],
            evidence_status="inferred",
            change_status="candidate",
        )
    if line == "motor":
        implausible = frame["licence_start_age_below_14_flag"]
        reason = pd.Series("derived_licence_start_age_below_14", index=frame.index)
        _append_ledger(
            ledgers,
            frame,
            implausible,
            source_file=source_file,
            field="years_licensed",
            original=frame["years_licensed"],
            derived=frame["licence_start_age_derived"],
            rule_id="missingness_and_availability",
            rule_version=1,
            reason=reason,
            evidence_status="unresolved",
            change_status="exception",
        )

    if len(frame) != len(source) or frame["row_id"].tolist() != original_ids:
        raise DataQualityError(f"{source_file}: row identity or ordering changed")
    if any(not frame[column].equals(source[column]) for column in original_columns):
        raise DataQualityError(f"{source_file}: an original source column changed")
    output_premium_total = float(frame["written_premium"].sum())
    if output_premium_total != original_premium_total:
        raise DataQualityError(f"{source_file}: written premium total changed")

    years = start.dt.year
    by_year: dict[str, Any] = {}
    for year in sorted(years.unique()):
        mask = years.eq(year)
        by_year[str(int(year))] = {
            "rows": int(mask.sum()),
            "exposure_raw_total": float(frame.loc[mask, "exposure_raw"].sum()),
            "exposure_clean_total": float(frame.loc[mask, "exposure_clean"].sum()),
            "exposure_changed_rows": int(frame.loc[mask, "exposure_changed"].sum()),
        }
    reconciliation = {
        "source_file": source_file,
        "line": line,
        "split": split,
        "rows_before": len(source),
        "rows_after": len(frame),
        "row_id_exact_order_preserved": frame["row_id"].tolist() == original_ids,
        "row_id_unique_and_non_null": bool(frame["row_id"].notna().all() and frame["row_id"].is_unique),
        "original_columns_preserved": True,
        "written_premium_total_before": original_premium_total,
        "written_premium_total_after": output_premium_total,
        "customer_id_changed_rows": int(frame["customer_id_changed"].sum()),
        "customer_id_reason_counts": {str(k): int(v) for k, v in frame["customer_id_reason"].value_counts(dropna=False).items()},
        "exposure_classification_counts": {str(k): int(v) for k, v in frame["exposure_classification"].value_counts(dropna=False).items()},
        "exposure_raw_total": float(frame["exposure_raw"].sum()),
        "exposure_clean_total": float(frame["exposure_clean"].sum()),
        "exposure_changed_rows": int(frame["exposure_changed"].sum()),
        "sum_insured_candidate_rows": int(frame["sum_insured_candidate_status"].eq("inferred").sum()),
        "customer_join_status": {str(k): int(v) for k, v in frame["customer_join_status"].value_counts().items()},
        "address_join_status": {str(k): int(v) for k, v in frame["address_join_status"].value_counts().items()},
        "weather_join_status": {str(k): int(v) for k, v in frame["weather_join_status"].value_counts().items()},
        "missingness_by_year": _missingness_by_year(source, years),
        "by_year": by_year,
    }
    if line == "motor":
        reconciliation["telematics_missing_reason_counts"] = {
            str(k): int(v) for k, v in frame["telematics_missing_reason"].value_counts(dropna=False).items()
        }
        reconciliation["licence_start_age_below_14_rows"] = int(frame["licence_start_age_below_14_flag"].sum())
    return frame, ledgers, reconciliation


def _publish_atomically(staging: Path, output_dir: Path) -> None:
    backup: Path | None = None
    if output_dir.exists():
        backup = output_dir.parent / f".{output_dir.name}.previous-{uuid.uuid4().hex}"
        output_dir.rename(backup)
    try:
        staging.rename(output_dir)
    except Exception:
        if backup is not None and backup.exists() and not output_dir.exists():
            backup.rename(output_dir)
        raise
    if backup is not None:
        shutil.rmtree(backup)


def prepare_data(
    *,
    data_dir: Path,
    output_dir: Path,
    cleaning_config_path: Path,
    reference_manifest_path: Path,
    project_root: Path,
) -> dict[str, Any]:
    """Build all six clean policy tables and reconciliation evidence."""
    data_dir = data_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    project_root = project_root.resolve()
    if output_dir == data_dir or data_dir in output_dir.parents or output_dir in data_dir.parents:
        raise DataQualityError("output directory must be separate from the raw input directory")
    config = json.loads(cleaning_config_path.read_text())
    reference = json.loads(reference_manifest_path.read_text())
    before_hashes = _input_hashes(data_dir, reference)
    code_digest, code_files = _code_digest(project_root, cleaning_config_path)
    previous_digest: str | None = None
    previous_manifest = output_dir / config["outputs"]["manifest"]
    if previous_manifest.is_file():
        previous_digest = json.loads(previous_manifest.read_text()).get(
            "logical_output_digest"
        )

    customers = pd.read_parquet(data_dir / "customers.parquet", columns=["customer_id"])
    addresses = pd.read_parquet(data_dir / "addresses.parquet", columns=["address_id"])
    weather = pd.read_parquet(data_dir / "weather.parquet", columns=["address_id", "year"])
    validate_unique_dimension(customers, ["customer_id"], name="customers")
    validate_unique_dimension(addresses, ["address_id"], name="addresses")
    validate_unique_dimension(weather, ["address_id", "year"], name="weather")
    customer_ids = pd.Index(customers["customer_id"])
    address_ids = pd.Index(addresses["address_id"])
    weather_keys = pd.MultiIndex.from_frame(weather[["address_id", "year"]])
    canonical_lengths = customers["customer_id"].str.len()
    if not canonical_lengths.eq(8).all() or not customers["customer_id"].str.fullmatch(r"[0-9]{8}").all():
        raise DataQualityError("customer reference is not entirely eight-character decimal text")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.staging-", dir=output_dir.parent))
    try:
        (staging / "data").mkdir()
        (staging / "ledger").mkdir()
        all_ledgers: list[pd.DataFrame] = []
        reconciliations: dict[str, Any] = {}
        output_hashes: dict[str, str] = {}
        for source_file in config["processing"]["order"]:
            line, split = POLICY_METADATA[source_file]
            source = pd.read_parquet(data_dir / source_file)
            cleaned, ledgers, reconciliation = _clean_policy(
                source,
                source_file=source_file,
                line=line,
                split=split,
                config=config,
                customer_ids=customer_ids,
                address_ids=address_ids,
                weather_keys=weather_keys,
            )
            relative = Path(config["outputs"]["policy_tables"][source_file])
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            cleaned.to_parquet(target, index=False, engine="pyarrow", compression="zstd")
            output_hashes[str(relative)] = sha256_file(target)
            all_ledgers.extend(ledgers)
            reconciliations[source_file] = reconciliation
            del source, cleaned

        ledger_columns = [
            "source_file", "row_id", "entity_key", "field", "original_value",
            "derived_value", "rule_id", "rule_version", "reason",
            "evidence_status", "change_status",
        ]
        ledger = pd.concat(all_ledgers, ignore_index=True) if all_ledgers else pd.DataFrame(columns=ledger_columns)
        ledger_path = staging / config["outputs"]["ledger"]
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger.to_parquet(ledger_path, index=False, engine="pyarrow", compression="zstd")
        output_hashes[config["outputs"]["ledger"]] = sha256_file(ledger_path)

        reconciliation = {
            "schema_version": 1,
            "config_id": config["config_id"],
            "source_hashes_match_reference": True,
            "canonical_customer_id": {
                "rows": len(customers),
                "unique": True,
                "null_count": 0,
                "format": "exactly eight decimal characters",
            },
            "dimension_keys": {
                "customers": {"rows": len(customers), "unique": True, "null_key_rows": 0},
                "addresses": {"rows": len(addresses), "unique": True, "null_key_rows": 0},
                "weather_address_year": {"rows": len(weather), "unique": True, "null_key_rows": 0},
            },
            "files": reconciliations,
            "ledger_rows": len(ledger),
            "claims_transformed": False,
            "dimensions_transformed": False,
        }
        reconciliation_path = staging / config["outputs"]["reconciliation"]
        reconciliation_path.write_text(json.dumps(reconciliation, indent=2, sort_keys=True) + "\n")
        output_hashes[config["outputs"]["reconciliation"]] = sha256_file(reconciliation_path)

        after_hashes = _input_hashes(data_dir, reference)
        if before_hashes != after_hashes:
            raise DataQualityError("raw input hashes changed during preparation")
        logical_digest = hashlib.sha256(
            json.dumps(output_hashes, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        manifest = {
            "schema_version": 1,
            "status": "complete",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config_id": config["config_id"],
            "source_reference_manifest": str(reference_manifest_path),
            "source_hashes_before": before_hashes,
            "source_hashes_after": after_hashes,
            "raw_hashes_unchanged": before_hashes == after_hashes,
            "outputs": output_hashes,
            "logical_output_digest": logical_digest,
            "rerun_comparison": {
                "previous_logical_output_digest": previous_digest,
                "matches_previous_run": (
                    previous_digest == logical_digest if previous_digest is not None else None
                ),
            },
            "code_digest": code_digest,
            "code_digest_files": code_files,
            "git_commit": os.environ.get("GIT_COMMIT", "not_asserted_uncommitted_code_digest_used"),
            "runtime": {
                "python": platform.python_version(),
                "implementation": sys.implementation.name,
                "pandas": pd.__version__,
                "pyarrow": pyarrow.__version__,
                "platform": platform.platform(),
            },
            "scope": "Step 2 policy preparation only; no claims target, model, prediction, or publication.",
        }
        manifest_path = staging / config["outputs"]["manifest"]
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        _publish_atomically(staging, output_dir)
        return manifest
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
