"""Frozen S6 production refit and fail-closed local submission boundary (S9).

No search, recalibration, target development or external write is implemented.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import time

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from iaa_hackathon.baselines import add_feature_blocks, fit_compact_glm
from iaa_hackathon.submission import SubmissionRules, validate_submission_frame


LINES = {"motor": "M", "buildings": "B", "contents": "C"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def save_json(path: Path, value: dict, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def check_hashes(mapping: dict[str, str]) -> None:
    for name, expected in mapping.items():
        if sha(Path(name)) != expected:
            raise ValueError(f"incompatible input/model hash: {name}")


def environment(lock: Path) -> dict:
    packages = {}
    for row in lock.read_text().splitlines():
        if not row.strip() or row.startswith("#"):
            continue
        name, expected = row.split("==")
        packages[name] = version(name)
        if packages[name] != expected:
            raise ValueError(f"environment mismatch: {name}")
    return {"python": platform.python_version(), "platform": platform.platform(), "packages": packages}


def preflight(config_path: Path, data_dir: Path) -> dict:
    cfg = read_json(config_path)
    check_hashes(cfg["inputs_sha256"] | cfg["code_sha256"])
    frozen = read_json(Path(cfg["benchmark_path"]))
    check_hashes(frozen["artifacts_sha256"])
    decision = read_json(Path(cfg["decision_path"]))
    if decision["decision"] != "retain_benchmark" or cfg["model_id"] != frozen["benchmark_id"]:
        raise ValueError("final selection does not follow frozen Step 8 evidence")
    for key in ("features", "blocks", "settings", "response_version"):
        if cfg[key] != frozen[key]:
            raise ValueError(f"frozen design changed: {key}")
    if read_json(Path("outputs/step8/acceptance.json"))["status"] != "passed":
        raise ValueError("Step 8 not accepted")
    check_hashes({str(data_dir / name): digest for name, digest in cfg["raw_sha256"].items()})
    env = environment(Path(cfg["environment_lock"]))
    if env["python"] != cfg["python"]:
        raise ValueError("Python version mismatch")
    if cfg["training_years"] != [2021, 2022, 2023, 2024] or cfg["floor"] is not None:
        raise ValueError("unsupported change to frozen production protocol")
    return {"status": "passed", "config_sha256": sha(config_path), "environment": env}


def data_view(cfg: dict, *, training: bool) -> pd.DataFrame:
    columns = {"row_id", "line", "period_start", "exposure_clean", "policy_id", "customer_id_clean", "sum_insured_raw", "sum_insured_repaired_flag"}
    columns.update(name for names in cfg["source_features"].values() for name in names)
    if training:
        columns.update(["observed_net_incurred", "observed_incurred", "observed_recoveries", "exposure_raw"])
    path = Path(cfg["training_path"] if training else cfg["test_path"])
    data = pd.read_parquet(path, columns=sorted(columns))
    if data.row_id.isna().any() or data.row_id.duplicated().any():
        raise ValueError("invalid source row identity")
    if set(data.line.unique()) != set(LINES):
        raise ValueError("unexpected source line universe")
    expected_years = set(cfg["training_years"] if training else [2025])
    if set(pd.to_datetime(data.period_start).dt.year.unique()) != expected_years:
        raise ValueError("ineligible source years")
    exposure = data.exposure_clean.to_numpy(float)
    if not np.isfinite(exposure).all() or (exposure <= 0).any():
        raise ValueError("invalid clean exposure")
    if training:
        y = data.observed_net_incurred.to_numpy(float)
        if not np.isfinite(y).all() or (y < 0).any():
            raise ValueError("invalid observed response")
        if not np.allclose(y, data.observed_incurred - data.observed_recoveries, rtol=0, atol=1e-7):
            raise ValueError("response components do not reconcile")
    return data


def predict_cost(model, frame: pd.DataFrame, line: str, cfg: dict) -> np.ndarray:
    x, features = add_feature_blocks(frame, line, cfg["blocks"][line])
    if features != cfg["features"][line] or list(model.feature_names_in_) != features:
        raise ValueError("saved feature schema mismatch")
    # This is the sole exposure multiplication at inference.
    rate = model.predict(x[features])
    cost = rate * frame.exposure_clean.to_numpy(float)
    if not np.isfinite(cost).all() or (cost <= 0).any():
        raise ValueError("invalid model period-cost prediction; no clipping")
    return cost


def check_equivalence(actual, expected, tolerance: dict) -> dict:
    a, b = np.asarray(actual, float), np.asarray(expected, float)
    if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("prediction shape or domain mismatch")
    if not np.allclose(a, b, **tolerance):
        raise ValueError("period-cost/reload mismatch (annual rates or double exposure forbidden)")
    return {"max_absolute_error": float(np.max(np.abs(a - b))), "exact_array_equal": bool(np.array_equal(a, b))}


def build_model(config_path: Path, data_dir: Path, output: Path) -> dict:
    verified = preflight(config_path, data_dir)
    cfg = read_json(config_path)
    manifest_path = output / "model-manifest.json"
    if manifest_path.exists():
        existing = read_json(manifest_path)
        if existing["config_sha256"] != verified["config_sha256"]:
            raise ValueError("existing model belongs to another configuration")
        check_hashes({str(output / p): h for p, h in existing["artifacts_sha256"].items()})
        return existing
    start = time.perf_counter()
    training, test = data_view(cfg, training=True), data_view(cfg, training=False)
    if len(training) != cfg["expected_training_rows"] or len(test) != cfg["expected_rows"]:
        raise ValueError("source counts changed")
    # Integer-minor-unit reconciliation independently checks the repaired claim universe.
    claims = pd.read_parquet(cfg["claims_path"], columns=["accepted_for_observed", "observed_net_incurred", "matched_row_id"])
    accepted = claims[claims.accepted_for_observed]
    claim_cents = accepted.assign(cents=np.rint(accepted.observed_net_incurred * 100).astype("int64")).groupby("matched_row_id").cents.sum()
    policy_cents = np.rint(training.observed_net_incurred * 100).astype("int64").to_numpy()
    if not np.array_equal(training.row_id.map(claim_cents).fillna(0).to_numpy(np.int64), policy_cents):
        raise ValueError("claims and training response universes differ")
    (output / "models").mkdir(parents=True, exist_ok=True)
    metadata, artifacts = {}, {}
    with threadpool_limits(limits=cfg["numerical_threads"]):
        for line in LINES:
            tr, te = training[training.line.eq(line)], test[test.line.eq(line)]
            pred, model, meta = fit_compact_glm(tr, te, line=line, blocks=cfg["blocks"][line], alpha=cfg["settings"]["alpha"], max_iter=cfg["settings"]["max_iter"])
            if not meta["converged"] or meta["features"] != cfg["features"][line]:
                raise ValueError("frozen GLM failed convergence/schema")
            actual_params = model.named_steps["model"].get_params()
            for key in ("power", "link", "alpha", "max_iter", "tol", "solver"):
                if actual_params[key] != cfg["settings"][key]:
                    raise ValueError(f"GLM parameter mismatch: {key}")
            path = output / "models" / f"{line}.joblib"
            if path.exists():
                raise ValueError("incomplete earlier run: refusing model overwrite")
            joblib.dump(model, path)
            reloaded = predict_cost(joblib.load(path), te, line, cfg)
            reload_check = check_equivalence(reloaded, pred, cfg["tolerance"])
            schema = output / "models" / f"{line}-schema.json"
            save_json(schema, {"source_features": cfg["source_features"][line], "features": meta["features"], "dtypes": {c: str(tr[c].dtype) for c in cfg["source_features"][line]}, "prediction_unit": "policy_period_cost"}, exclusive=True)
            artifacts[str(path.relative_to(output))] = sha(path)
            artifacts[str(schema.relative_to(output))] = sha(schema)
            metadata[line] = {**meta, "training_rows": len(tr), "test_rows": len(te), "training_exposure": float(tr.exposure_clean.sum()), "test_exposure": float(te.exposure_clean.sum()), "observed_total": float(tr.observed_net_incurred.sum()), "prediction_total": float(pred.sum()), "reload": reload_check}
    result = {"status": "complete", "generation_utc": datetime.now(timezone.utc).isoformat(), "run_id": verified["config_sha256"][:16], "config_sha256": verified["config_sha256"], "model_id": cfg["model_id"], "response_version": cfg["response_version"], "training_years": cfg["training_years"], "environment": verified["environment"], "lines": metadata, "artifacts_sha256": artifacts, "runtime_seconds": time.perf_counter() - start, "claim_response_cents_reconciled": True, "production_fits": 3}
    save_json(manifest_path, result, exclusive=True)
    return result


def model_predictions(cfg: dict, output: Path, test: pd.DataFrame) -> np.ndarray:
    manifest = read_json(output / "model-manifest.json")
    check_hashes({str(output / p): h for p, h in manifest["artifacts_sha256"].items()})
    predictions = np.empty(len(test), float)
    with threadpool_limits(limits=cfg["numerical_threads"]):
        for line in LINES:
            mask = test.line.eq(line).to_numpy()
            predictions[mask] = predict_cost(joblib.load(output / "models" / f"{line}.joblib"), test.loc[mask], line, cfg)
    return predictions


def validate_final(candidate: pd.DataFrame, sample_ids: list[str], test: pd.DataFrame, expected_cost: np.ndarray, cfg: dict) -> dict:
    checks = validate_submission_frame(candidate, sample_ids, SubmissionRules(expected_rows=cfg["expected_rows"], strict_positive=True))
    if not checks["order_matches_sample"]:
        raise ValueError("CSV is not in exact sample order")
    if test.row_id.isna().any() or test.row_id.duplicated().any() or set(test.row_id) != set(sample_ids):
        raise ValueError("test/sample identities differ")
    reference = test[["row_id", "line"]].assign(expected_cost=expected_cost)
    aligned = candidate.merge(reference, on="row_id", how="left", validate="one_to_one", sort=False)
    for line, prefix in LINES.items():
        mask = aligned.line.eq(line)
        if not aligned.loc[mask, "row_id"].str.startswith(prefix).all():
            raise ValueError("line prefix mismatch")
    equivalence = check_equivalence(aligned.prediction.to_numpy(), aligned.expected_cost.to_numpy(), cfg["tolerance"])
    return {**checks, "no_serialized_index": True, "numeric_finite_nonnegative_strict_positive": True, "line_prefixes_and_counts_reconciled": True, "counts_by_line": aligned.groupby("line").size().to_dict(), "saved_model_period_cost_equivalence": equivalence, "annual_rates_rejected": True, "exposure_applied_exactly_once": True, "prediction_floor_applied": False}


def csv_path(cfg: dict, config_path: Path, directory: Path) -> Path:
    return directory / f"part1_S6_glm_{cfg['response_version']}_{sha(config_path)[:16]}.csv"


def build_csv(config_path: Path, data_dir: Path, output: Path, directory: Path) -> dict:
    preflight(config_path, data_dir)
    cfg = read_json(config_path)
    manifest = read_json(output / "model-manifest.json")
    if manifest["config_sha256"] != sha(config_path):
        raise ValueError("model/config identity mismatch")
    test = data_view(cfg, training=False)
    prediction = model_predictions(cfg, output, test)
    for line in LINES:
        raw = pd.read_parquet(data_dir / f"test_{line}.parquet", columns=["row_id", "exposure", "period_start"])
        repaired = test[test.line.eq(line)]
        if len(raw) != cfg["expected_test_rows_by_line"][line] or raw.row_id.tolist() != repaired.row_id.tolist():
            raise ValueError("raw/repaired test identities or line counts differ")
        if not np.array_equal(raw.exposure.to_numpy(float), repaired.exposure_clean.to_numpy(float)):
            raise ValueError("test exposure differs from original test source")
        if not pd.to_datetime(raw.period_start).dt.year.eq(2025).all():
            raise ValueError("raw test year is not 2025")
    sample = pd.read_parquet(data_dir / cfg["sample_filename"], columns=["row_id"])
    # Explicit validated 1:1 join: left/sample order is the final serialization order.
    candidate = sample.merge(test[["row_id"]].assign(prediction=prediction), on="row_id", how="left", validate="one_to_one", sort=False)
    validate_final(candidate, sample.row_id.tolist(), test, prediction, cfg)
    path = csv_path(cfg, config_path, directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        candidate.to_csv(path, mode="x", index=False, float_format="%.17g", lineterminator="\n", encoding="utf-8")
    # Existing files are never rewritten: a changed row/value fails verification.
    reread = pd.read_csv(path, dtype={"row_id": str}, float_precision="round_trip")
    checks = validate_final(reread, sample.row_id.tolist(), test, prediction, cfg)
    result = {"status": "passed", "csv_path": str(path.resolve()), "csv_sha256": sha(path), "rows": len(reread), "prediction_total": float(reread.prediction.sum()), "prediction_totals_by_line": reread.assign(line=reread.row_id.str[0].map({v: k for k, v in LINES.items()})).groupby("line").prediction.sum().to_dict(), "mechanical_gates": checks}
    save_json(output / "verification.json", result)
    return result


def git_snapshot(output: Path) -> dict:
    def git(*args):
        return subprocess.check_output(["git", *args])
    patch = git("diff", "HEAD", "--binary")
    untracked = {}
    for name in git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0"):
        if name:
            untracked[name] = sha(Path(name))
    combined = hashlib.sha256(patch + json.dumps(untracked, sort_keys=True).encode()).hexdigest()
    # Content-address the snapshot. A later documentation change must never
    # overwrite evidence referenced by an already-issued immutable manifest.
    directory = output / "provenance" / combined
    directory.mkdir(parents=True, exist_ok=True)
    register = directory / "untracked-sha256.json"
    if register.exists():
        if read_json(register) != untracked:
            raise ValueError("existing immutable untracked register differs")
    else:
        save_json(register, untracked, exclusive=True)
    path = directory / "working-tree.patch"
    if path.exists():
        if path.read_bytes() != patch:
            raise ValueError("existing immutable patch differs")
    else:
        with path.open("xb") as stream:
            stream.write(patch)
    return {"head": git("rev-parse", "HEAD").decode().strip(), "branch": git("branch", "--show-current").decode().strip(), "origin": git("remote", "get-url", "origin").decode().strip(), "dirty": bool(git("status", "--porcelain")), "status_porcelain": git("status", "--porcelain").decode(), "tracked_patch_sha256": hashlib.sha256(patch).hexdigest(), "untracked_files_sha256": untracked, "combined_worktree_sha256": combined, "snapshot_artifacts_sha256": {str(path.resolve()): sha(path), str(register.resolve()): sha(register)}, "snapshot_time_utc": datetime.now(timezone.utc).isoformat()}
