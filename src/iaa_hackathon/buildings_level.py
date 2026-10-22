"""Buildings-only credibility-shrunk aggregate calibration adjustment."""
from __future__ import annotations

import numpy as np
import pandas as pd


def aggregate_ae(actual: np.ndarray, prediction: np.ndarray) -> float:
    """Return aggregate actual / predicted for aligned nonnegative values."""
    y = np.asarray(actual, dtype=float)
    p = np.asarray(prediction, dtype=float)
    if y.ndim != 1 or p.shape != y.shape or not len(y):
        raise ValueError("actual and prediction must be nonempty, aligned vectors")
    if (not np.isfinite(y).all() or not np.isfinite(p).all()
            or (y < 0).any() or (p < 0).any() or p.sum() <= 0):
        raise ValueError("A/E inputs must be finite and nonnegative with positive prediction total")
    return float(y.sum() / p.sum())


def exposure_weighted_average_ae(aes: dict[str, float], exposures: dict[str, float]) -> float:
    """Average fold A/Es using each fold's total cleaned exposure as its weight."""
    if set(aes) != set(exposures) or not aes:
        raise ValueError("A/E and exposure folds must have identical nonempty keys")
    ae_values = np.asarray(list(aes.values()), dtype=float)
    exposure_values = np.asarray([exposures[key] for key in aes], dtype=float)
    if (not np.isfinite(ae_values).all() or (ae_values < 0).any()
            or not np.isfinite(exposure_values).all() or (exposure_values <= 0).any()):
        raise ValueError("A/E and fold exposure weights must be finite and nonnegative/positive")
    return float(np.average(ae_values, weights=exposure_values))


def calculate_uplift(
    average_ae: float,
    *,
    credibility: float = 0.5,
    upper_cap: float = 1.05,
) -> dict[str, float | bool]:
    """Shrink the observed A/E gap toward 1 and apply the stated upper cap."""
    if (not np.isfinite(average_ae) or average_ae < 0
            or not np.isfinite(credibility) or not 0 <= credibility <= 1
            or not np.isfinite(upper_cap) or upper_cap <= 0):
        raise ValueError("uplift inputs are invalid")
    raw = 1.0 + credibility * (average_ae - 1.0)
    factor = min(raw, upper_cap)
    if factor < 0:
        raise ValueError("uplift factor must be nonnegative")
    return {
        "uncapped_factor": float(raw),
        "factor": float(factor),
        "cap_binding": bool(raw > upper_cap),
    }


def apply_buildings_uplift(
    submission: pd.DataFrame,
    factor: float,
    *,
    building_prefix: str = "B",
) -> pd.DataFrame:
    """Scale building rows only, preserving order and all non-building values."""
    if submission.columns.tolist() != ["row_id", "prediction"]:
        raise ValueError("submission must have exactly row_id,prediction columns")
    if (submission.row_id.isna().any() or submission.row_id.duplicated().any()
            or not np.isfinite(factor) or factor < 0):
        raise ValueError("submission IDs or uplift factor are invalid")
    predictions = submission.prediction.to_numpy(dtype=float)
    if not np.isfinite(predictions).all() or (predictions < 0).any():
        raise ValueError("parent predictions must be finite and nonnegative")
    selected = submission.row_id.astype("string").str.startswith(building_prefix).to_numpy()
    if not selected.any():
        raise ValueError("no building rows found for the configured ID prefix")
    result = submission.copy()
    result.loc[selected, "prediction"] = predictions[selected] * factor
    if (not np.isfinite(result.prediction.to_numpy(float)).all()
            or (result.prediction < 0).any()
            or not np.array_equal(result.loc[~selected, "prediction"].to_numpy(float),
                                  predictions[~selected])):
        raise ValueError("uplift produced invalid predictions or changed other lines")
    return result
