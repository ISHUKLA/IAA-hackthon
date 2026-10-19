"""Synthetic adversarial tests for the final CSV and provenance boundary."""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.baselines import fit_compact_glm
from iaa_hackathon.final_submission import check_equivalence, check_hashes, predict_cost, sha, validate_final


@pytest.fixture
def boundary():
    test = pd.DataFrame({"row_id": ["M0001", "B0002", "C0003"], "line": ["motor", "buildings", "contents"], "exposure_clean": [.25, .5, 1.]})
    candidate = pd.DataFrame({"row_id": test.row_id, "prediction": [25., 50., 100.]})
    cfg = {"expected_rows": 3, "tolerance": {"rtol": 1e-12, "atol": 1e-10}}
    return test, candidate, cfg


def test_valid_and_roundtrip(boundary, tmp_path):
    test, frame, cfg = boundary
    path = tmp_path / "candidate.csv"
    frame.to_csv(path, index=False, float_format="%.17g")
    read = pd.read_csv(path, dtype={"row_id": str}, float_precision="round_trip")
    check = validate_final(read, frame.row_id.tolist(), test, frame.prediction.to_numpy(), cfg)
    assert check["saved_model_period_cost_equivalence"]["exact_array_equal"]
    assert check["counts_by_line"] == {"motor": 1, "buildings": 1, "contents": 1}


@pytest.mark.parametrize("fault", ["duplicate", "missing", "extra", "reordered", "index", "nan", "inf", "negative", "zero", "annual_rate", "double_exposure", "null_id", "numeric_id", "nonnumeric", "boolean"])
def test_fail_closed(boundary, fault):
    test, original, cfg = boundary
    frame = original.copy()
    if fault == "duplicate":
        frame.loc[1, "row_id"] = frame.loc[0, "row_id"]
    elif fault == "missing":
        frame = frame.iloc[:-1]
    elif fault == "extra":
        frame.loc[2, "row_id"] = "Cextra"
    elif fault == "reordered":
        frame = frame.iloc[::-1]
    elif fault == "index":
        frame.insert(0, "Unnamed: 0", range(len(frame)))
    elif fault in ("nan", "inf", "negative", "zero"):
        frame.loc[0, "prediction"] = {"nan": np.nan, "inf": np.inf, "negative": -1, "zero": 0}[fault]
    elif fault == "annual_rate":
        frame["prediction"] = frame.prediction / test.exposure_clean
    elif fault == "double_exposure":
        frame["prediction"] *= test.exposure_clean
    elif fault == "null_id":
        frame.loc[0, "row_id"] = None
    elif fault == "numeric_id":
        frame["row_id"] = [1, 2, 3]
    elif fault == "nonnumeric":
        frame["prediction"] = ["25", "bad", "100"]
    elif fault == "boolean":
        frame["prediction"] = True
    with pytest.raises(ValueError):
        validate_final(frame, original.row_id.tolist(), test, original.prediction.to_numpy(), cfg)


def test_prefix_and_source_duplicates_fail(boundary):
    test, frame, cfg = boundary
    test.loc[0, "line"] = "contents"
    with pytest.raises(ValueError, match="prefix"):
        validate_final(frame, frame.row_id.tolist(), test, frame.prediction.to_numpy(), cfg)
    test.loc[1, "row_id"] = "M0001"
    with pytest.raises(ValueError, match="identities"):
        validate_final(frame, frame.row_id.tolist(), test, frame.prediction.to_numpy(), cfg)


def test_input_and_model_hash_mismatch(tmp_path):
    path = tmp_path / "model.joblib"
    path.write_bytes(b"original")
    expected = sha(path)
    check_hashes({str(path): expected})
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="incompatible input/model hash"):
        check_hashes({str(path): expected})


def test_nonfinite_reference_and_wrong_shape_fail():
    for expected in ([np.inf], [np.nan], [1, 2]):
        with pytest.raises(ValueError):
            check_equivalence([1], expected, {"rtol": 1e-12, "atol": 1e-10})


def test_git_snapshot_never_overwrites_prior_evidence(tmp_path, monkeypatch):
    from iaa_hackathon.final_submission import git_snapshot
    import subprocess
    monkeypatch.chdir(tmp_path)
    patch = [b"first diff"]
    def fake_git(command):
        if command[1] == "diff":
            return patch[0]
        if command[1] == "ls-files":
            return b""
        return b"synthetic-dirty-state"
    monkeypatch.setattr(subprocess, "check_output", fake_git)
    first = git_snapshot(tmp_path / "output")
    before = dict(first["snapshot_artifacts_sha256"])
    patch[0] = b"later documentation diff"
    second = git_snapshot(tmp_path / "output")
    assert first["combined_worktree_sha256"] != second["combined_worktree_sha256"]
    check_hashes(before)
    assert git_snapshot(tmp_path / "output")["snapshot_artifacts_sha256"] == second["snapshot_artifacts_sha256"]


def test_train_only_preprocessing_and_reload(tmp_path):
    # A held-out extreme age/category must not enter fitted imputation/vocabulary.
    rng = np.random.default_rng(42)
    n = 300
    train = pd.DataFrame({"driver_age": rng.integers(20, 70, n).astype(float), "years_licensed": rng.integers(2, 15, n), "vehicle_age": rng.integers(0, 15, n).astype(float), "annual_mileage": rng.integers(1000, 15000, n).astype(float), "voluntary_excess": 200, "compulsory_excess": 100, "cover_type": "basic", "vehicle_use": "private", "body_type": "saloon", "engine_size_cc": 1400., "exposure_clean": rng.uniform(.2, 1, n), "observed_net_incurred": rng.gamma(1, 150, n)})
    train.loc[0, "driver_age"] = np.nan
    test = train.iloc[:4].copy()
    test["cover_type"] = "unseen"
    test["driver_age"] = 999
    blocks = ["age_nonlinearity", "ordinary_missingness"]
    predicted, model, meta = fit_compact_glm(train, test, line="motor", blocks=blocks)
    cfg = {"features": {"motor": meta["features"]}, "blocks": {"motor": blocks}}
    fitted_imputer = model.named_steps["transform"].named_transformers_["numeric"].named_steps["impute"]
    assert fitted_imputer.statistics_[0] == train.driver_age.median()
    encoder = model.named_steps["transform"].named_transformers_["categorical"].named_steps["onehot"]
    assert all("unseen" not in values for values in encoder.categories_)
    path = tmp_path / "model.joblib"
    joblib.dump(model, path)
    reload = predict_cost(joblib.load(path), test, "motor", cfg)
    assert np.array_equal(predicted, reload)
    # The rate is invariant when only inference exposure changes.
    test2 = test.copy()
    test2["exposure_clean"] *= .5
    assert np.allclose(predict_cost(model, test2, "motor", cfg), .5 * predicted, rtol=1e-14)
