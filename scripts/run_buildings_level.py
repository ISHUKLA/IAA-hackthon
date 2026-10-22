#!/usr/bin/env python3
"""Apply a half-gap, exposure-weighted buildings A/E uplift to a saved candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd

from iaa_hackathon.baselines import score_vector
from iaa_hackathon.buildings_level import (
    aggregate_ae,
    apply_buildings_uplift,
    calculate_uplift,
    exposure_weighted_average_ae,
)
from iaa_hackathon.submission import SubmissionRules, validate_submission_frame


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _metric(actual: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    score = score_vector(np.asarray(actual, float), np.asarray(prediction, float))
    return {
        "rows": int(score["rows"]),
        "d2_tweedie_power_1_5": float(score["d2_tweedie_score"]),
        "mean_tweedie_deviance": float(score["mean_tweedie_deviance"]),
        "actual_total": float(np.sum(actual)),
        "predicted_total": float(np.sum(prediction)),
        "ae_actual_over_predicted": aggregate_ae(actual, prediction),
    }


def _verify_source(path: Path, expected: str, label: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"{label} hash differs: expected {expected}, got {actual}")
    return actual


def _fold_experience(
    fold: str,
    prediction_path: Path,
    expected_prediction_hash: str,
    parent: dict,
    training_path: Path,
    prediction_column: str,
    exposure_column: str,
) -> tuple[dict, pd.DataFrame, str]:
    prediction_hash = _verify_source(prediction_path, expected_prediction_hash, f"{fold} predictions")
    prediction = pd.read_parquet(prediction_path)
    required = {"row_id", "line", "actual", prediction_column}
    if not required.issubset(prediction.columns):
        raise ValueError(f"{fold} saved predictions lack {sorted(required - set(prediction.columns))}")
    if prediction.row_id.isna().any() or prediction.row_id.duplicated().any():
        raise ValueError(f"{fold} saved prediction IDs are not unique")
    building = prediction.loc[prediction.line.eq("buildings"), ["row_id", "actual", prediction_column]].copy()
    identity = parent["fold_identity"][fold]["buildings"]
    row_fingerprint = hashlib.sha256("\n".join(building.row_id.tolist()).encode()).hexdigest()
    target_fingerprint = hashlib.sha256(building.actual.to_numpy("<f8").tobytes()).hexdigest()
    if len(building) != int(identity["rows"]):
        raise ValueError(f"{fold} buildings row count differs from parent identity")
    if row_fingerprint != identity["row_id_sha256"] or target_fingerprint != identity["target_sha256"]:
        raise ValueError(f"{fold} buildings row IDs or target fingerprint differs from parent")
    table = pd.read_parquet(training_path, columns=["row_id", "line", exposure_column])
    if table.row_id.isna().any() or table.row_id.duplicated().any():
        raise ValueError("training model table contains duplicate or missing row IDs")
    exposures = table.loc[table.line.eq("buildings"), ["row_id", exposure_column]]
    building = building.merge(exposures, on="row_id", how="left", validate="one_to_one", sort=False)
    exposure = building[exposure_column].to_numpy(float)
    if (not np.isfinite(exposure).all() or (exposure <= 0).any()):
        raise ValueError(f"{fold} buildings exposure is missing, nonfinite, or nonpositive")
    actual = building.actual.to_numpy(float)
    forecast = building[prediction_column].to_numpy(float)
    ae = aggregate_ae(actual, forecast)
    exposure_total = float(exposure.sum())
    metrics = {
        "fold": fold,
        "rows": len(building),
        "actual_total": float(actual.sum()),
        "predicted_total": float(forecast.sum()),
        "ae_actual_over_predicted": ae,
        "exposure_column": exposure_column,
        "exposure_total": exposure_total,
        "row_id_sha256": row_fingerprint,
        "target_sha256": target_fingerprint,
        "saved_prediction_sha256": prediction_hash,
    }
    return metrics, building, prediction_hash


def run(data_dir: Path, config_path: Path, output_dir: Path) -> dict:
    started = time.perf_counter()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing output directory: {output_dir}")
    cfg = read_json(config_path)
    parent_dir = Path(cfg["parent_dir"])
    parent_manifest_path = parent_dir / "manifest.json"
    parent_csv_path = parent_dir / "submission.csv"
    parent_manifest_hash = _verify_source(
        parent_manifest_path, cfg["parent_manifest_sha256"], "home parent manifest")
    parent_csv_hash = _verify_source(
        parent_csv_path, cfg["parent_csv_sha256"], "home parent submission")
    parent = read_json(parent_manifest_path)
    if parent.get("target_version") != "conditional-ultimate-v1":
        raise ValueError("unexpected parent target version")
    if parent.get("csv", {}).get("sha256") != parent_csv_hash:
        raise ValueError("parent manifest does not identify the checked parent CSV")

    training_path = Path(parent["source_paths"]["training"])
    training_hash = _verify_source(training_path, parent["source_sha256"]["training"], "training table")
    test_model_path = Path(parent["source_paths"]["test"])
    _verify_source(test_model_path, parent["source_sha256"]["test"], "repaired test table")
    sample_path = data_dir / "sample_submission.parquet"
    _verify_source(sample_path, parent["source_sha256"]["sample"], "sample submission")
    sample = pd.read_parquet(sample_path, columns=["row_id"])
    sample_ids = sample.row_id.tolist()
    rules = SubmissionRules(expected_rows=int(cfg["expected_rows"]), strict_positive=False)
    candidate_parent = pd.read_csv(parent_csv_path, dtype={"row_id": str}, float_precision="round_trip")
    parent_checks = validate_submission_frame(candidate_parent, sample_ids, rules)
    if not parent_checks["order_matches_sample"]:
        raise ValueError("parent CSV does not follow exact sample order")

    fold_metrics: dict[str, dict] = {}
    fold_frames: dict[str, pd.DataFrame] = {}
    prediction_hashes: dict[str, str] = {}
    for fold in cfg["folds"]:
        rel = f"outputs/home-catboost-retune-v1/predictions/{fold}-pooled.parquet"
        path = Path(rel)
        expected_hash = parent["prediction_sha256"][rel]
        metrics, aligned, digest = _fold_experience(
            fold, path, expected_hash, parent, training_path,
            cfg["prediction_column"], cfg["training_exposure_column"],
        )
        fold_metrics[fold] = metrics
        fold_frames[fold] = aligned
        prediction_hashes[rel] = digest

    aes = {fold: values["ae_actual_over_predicted"] for fold, values in fold_metrics.items()}
    exposure_weights = {fold: values["exposure_total"] for fold, values in fold_metrics.items()}
    average_ae = exposure_weighted_average_ae(aes, exposure_weights)
    uplift = calculate_uplift(
        average_ae, credibility=float(cfg["credibility"]), upper_cap=float(cfg["upper_cap"])
    )
    factor = float(uplift["factor"])

    local_scores = {}
    prediction_column = cfg["prediction_column"]
    for fold in cfg["folds"]:
        all_rows = pd.read_parquet(f"outputs/home-catboost-retune-v1/predictions/{fold}-pooled.parquet")
        actual = all_rows.actual.to_numpy(float)
        parent_prediction = all_rows[prediction_column].to_numpy(float)
        candidate_prediction = parent_prediction.copy()
        candidate_prediction[all_rows.line.eq("buildings").to_numpy()] *= factor
        line_scores = {}
        for line in ("buildings", "pooled"):
            mask = all_rows.line.eq("buildings").to_numpy() if line == "buildings" else np.ones(len(all_rows), dtype=bool)
            old_metric = _metric(actual[mask], parent_prediction[mask])
            new_metric = _metric(actual[mask], candidate_prediction[mask])
            line_scores[line] = {
                "parent": old_metric,
                "candidate": new_metric,
                "delta_d2": new_metric["d2_tweedie_power_1_5"] - old_metric["d2_tweedie_power_1_5"],
            }
        local_scores[fold] = {"circular_not_a_gate": True, **line_scores}

    output = apply_buildings_uplift(candidate_parent, factor,
                                    building_prefix=cfg["line_prefixes"]["buildings"])
    checks = validate_submission_frame(output, sample_ids, rules)
    if not checks["order_matches_sample"]:
        raise ValueError("candidate row order differs from sample")
    for line in ("motor", "contents"):
        prefix = cfg["line_prefixes"][line]
        mask = candidate_parent.row_id.str.startswith(prefix).to_numpy()
        if not np.array_equal(output.loc[mask, "prediction"].to_numpy(float),
                              candidate_parent.loc[mask, "prediction"].to_numpy(float)):
            raise ValueError(f"{line} predictions changed")
    building_mask = output.row_id.str.startswith(cfg["line_prefixes"]["buildings"])
    if not np.array_equal(
        output.loc[building_mask, "prediction"].to_numpy(float),
        candidate_parent.loc[building_mask, "prediction"].to_numpy(float) * factor,
    ):
        raise ValueError("buildings predictions do not equal parent multiplied by factor")

    raw_test_counts = {}
    for line, prefix in cfg["line_prefixes"].items():
        raw_path = data_dir / f"test_{line}.parquet"
        expected = parent["csv"]["checks"]["per_line_raw_test_coverage"][line]["raw_test_sha256"]
        _verify_source(raw_path, expected, f"raw {line} test")
        raw_ids = pd.read_parquet(raw_path, columns=["row_id"]).row_id
        candidate_ids = output.loc[output.row_id.str.startswith(prefix), "row_id"]
        if len(raw_ids) != len(candidate_ids) or set(raw_ids) != set(candidate_ids):
            raise ValueError(f"{line} candidate coverage differs from raw test IDs")
        raw_test_counts[line] = len(raw_ids)

    parent_means, candidate_means = {}, {}
    for line, prefix in cfg["line_prefixes"].items():
        mask = candidate_parent.row_id.str.startswith(prefix)
        parent_means[line] = float(candidate_parent.loc[mask, "prediction"].mean())
        candidate_means[line] = float(output.loc[mask, "prediction"].mean())
    if parent_means["buildings"] <= 0:
        raise ValueError("parent buildings mean must be positive")

    output_dir.mkdir(parents=True, exist_ok=False)
    csv_path = output_dir / "submission.csv"
    output.to_csv(csv_path, mode="x", index=False, float_format="%.17g", lineterminator="\n")
    reread = pd.read_csv(csv_path, dtype={"row_id": str}, float_precision="round_trip")
    reread_checks = validate_submission_frame(reread, sample_ids, rules)
    if (not reread_checks["order_matches_sample"]
            or not np.array_equal(reread.prediction.to_numpy(float), output.prediction.to_numpy(float))):
        raise ValueError("serialized submission differs from verified frame")
    for line, prefix in (("motor", "M"), ("contents", "C")):
        mask = reread.row_id.str.startswith(prefix)
        parent_mask = candidate_parent.row_id.str.startswith(prefix)
        if not np.array_equal(reread.loc[mask, "prediction"].to_numpy(float),
                              candidate_parent.loc[parent_mask, "prediction"].to_numpy(float)):
            raise ValueError(f"serialized {line} values are not identical to parent")

    # Recheck immutable inputs after candidate serialization.
    _verify_source(parent_manifest_path, cfg["parent_manifest_sha256"], "home parent manifest")
    _verify_source(parent_csv_path, cfg["parent_csv_sha256"], "home parent submission")
    input_paths = {
        "config": config_path,
        "runner": Path(__file__),
        "helper": Path("src/iaa_hackathon/buildings_level.py"),
        "parent_manifest": parent_manifest_path,
        "parent_csv": parent_csv_path,
        "training_table": training_path,
        "repaired_test_table": test_model_path,
        "sample_submission": sample_path,
        **{f"{fold}_predictions": Path(path) for fold, path in (("F2023", "outputs/home-catboost-retune-v1/predictions/F2023-pooled.parquet"), ("F2024", "outputs/home-catboost-retune-v1/predictions/F2024-pooled.parquet"))},
        **{f"raw_test_{line}": data_dir / f"test_{line}.parquet" for line in cfg["line_prefixes"]},
    }
    input_hashes = {name: sha256(path) for name, path in input_paths.items()}
    manifest = {
        "experiment": cfg["experiment"],
        "status": "exploratory_level_uplift_built_at_explicit_user_request",
        "parent": "home-catboost-retune-v1",
        "target_version": parent["target_version"],
        "human_decision": "",
        "D2_2025": None,
        "method": {
            "a_e_definition": "aggregate actual / aggregate predicted",
            "folds": list(cfg["folds"]),
            "a_e_by_fold": fold_metrics,
            "average": {
                "method": "exposure-weighted average of the two fold aggregate A/Es",
                "formula": "sum_fold(AE_fold * sum(exposure_clean_fold)) / sum_fold(sum(exposure_clean_fold))",
                "value": average_ae,
                "fold_exposure_weights": exposure_weights,
            },
            "credibility": float(cfg["credibility"]),
            "uncapped_factor": float(uplift["uncapped_factor"]),
            "upper_cap": float(cfg["upper_cap"]),
            "factor": factor,
            "cap_binding": bool(uplift["cap_binding"]),
            "application": "multiply parent 2025 buildings period-cost predictions by factor after the parent trend; motor and contents are copied unchanged",
        },
        "local_scores": {
            "metric": "local conditional-ultimate-v1 Tweedie D2, power 1.5",
            "interpretation": "circular transparency only; the multiplier was derived from these same F2023/F2024 actual/predicted ratios and these scores are not an acceptance gate",
            "folds": local_scores,
        },
        "mean_review": {
            "parent_2025_mean_by_line": parent_means,
            "candidate_2025_mean_by_line": candidate_means,
            "building_mean_change_percent": 100.0 * (candidate_means["buildings"] / parent_means["buildings"] - 1.0),
            "motor_and_contents_exactly_identical": True,
        },
        "input_paths": {name: str(path.resolve()) for name, path in input_paths.items()},
        "input_sha256": input_hashes,
        "output": {
            "path": str(csv_path.resolve()),
            "sha256": sha256(csv_path),
            "rows": len(reread),
            "columns": list(reread.columns),
            "checks": {**checks, "reread": reread_checks,
                       "raw_test_id_counts": raw_test_counts,
                       "raw_test_coverage_exact": True,
                       "motor_predictions_identical_to_parent": True,
                       "contents_predictions_identical_to_parent": True,
                       "buildings_equal_parent_times_factor": True},
            "prediction_min": float(reread.prediction.min()),
            "prediction_max": float(reread.prediction.max()),
        },
        "runtime_seconds": time.perf_counter() - started,
    }
    manifest_path = output_dir / "manifest.json"
    with manifest_path.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True,
                        help="Directory containing sample_submission.parquet and test_{line}.parquet")
    parser.add_argument("--config", type=Path, default=Path("configs/buildings_level_v1.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/buildings-level-v1"))
    args = parser.parse_args()
    result = run(args.data_dir, args.config, args.output_dir)
    print(json.dumps({"method": result["method"], "local_scores": result["local_scores"],
                      "mean_review": result["mean_review"], "output": result["output"],
                      "runtime_seconds": result["runtime_seconds"]}, indent=2), flush=True)
