"""Step 5 compact baselines and Step 6 bounded feature blocks."""
from __future__ import annotations

import time
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import TweedieRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from iaa_hackathon.metrics import metric_report


BASE_FEATURES = {
    "motor": ["driver_age", "years_licensed", "vehicle_age", "annual_mileage", "voluntary_excess", "compulsory_excess", "cover_type", "vehicle_use", "body_type"],
    "buildings": ["policyholder_age", "sum_insured_repaired", "days_unoccupied", "voluntary_excess", "compulsory_excess", "construction_type_standardized", "occupancy"],
    "contents": ["policyholder_age", "sum_insured_repaired", "voluntary_excess", "compulsory_excess", "tenure", "security_level", "accidental_damage_cover"],
}

BLOCK_FEATURES = {
    "motor": {
        "age_nonlinearity": ["driver_age_squared", "licensing_age"],
        "vehicle_mileage": ["mileage_per_vehicle_year"],
        "ordinary_missingness": ["annual_mileage_missing", "vehicle_age_missing", "engine_size_cc_missing"],
    },
    "buildings": {
        "log_sum_insured": ["log_sum_insured"],
        "occupancy_security": ["smoke_alarms", "accidental_damage_cover", "days_unoccupied_missing"],
        "construction_interaction": ["construction_occupancy"],
    },
    "contents": {
        "log_sum_insured": ["log_sum_insured"],
        "household_use": ["works_from_home", "lodgers", "bicycle_cover"],
        "security_value": ["high_value_items", "security_high_value"],
    },
}


def add_feature_blocks(frame: pd.DataFrame, line: str, blocks: list[str]) -> tuple[pd.DataFrame, list[str]]:
    out = frame.copy()
    features = list(BASE_FEATURES[line])
    for block in blocks:
        if block not in BLOCK_FEATURES[line]:
            raise ValueError(f"unknown feature block {line}/{block}")
        if block == "age_nonlinearity":
            out["driver_age_squared"] = pd.to_numeric(out["driver_age"], errors="coerce") ** 2
            out["licensing_age"] = pd.to_numeric(out["driver_age"], errors="coerce") - pd.to_numeric(out["years_licensed"], errors="coerce")
        elif block == "vehicle_mileage":
            out["mileage_per_vehicle_year"] = pd.to_numeric(out["annual_mileage"], errors="coerce") / (pd.to_numeric(out["vehicle_age"], errors="coerce").clip(lower=0) + 1)
        elif block == "ordinary_missingness":
            for source in ("annual_mileage", "vehicle_age", "engine_size_cc"):
                out[f"{source}_missing"] = out[source].isna().astype("int8")
        elif block == "log_sum_insured":
            insured = pd.to_numeric(out["sum_insured_repaired"], errors="coerce")
            out["log_sum_insured"] = np.log1p(insured.where(insured >= 0))
        elif block == "occupancy_security":
            out["days_unoccupied_missing"] = out["days_unoccupied"].isna().astype("int8")
        elif block == "construction_interaction":
            out["construction_occupancy"] = out["construction_type_standardized"].astype("string").fillna("missing") + "__" + out["occupancy"].astype("string").fillna("missing")
        elif block == "security_value":
            out["security_high_value"] = out["security_level"].astype("string").fillna("missing") + "__" + out["high_value_items"].astype("string").fillna("missing")
        features.extend(BLOCK_FEATURES[line][block])
    return out, list(dict.fromkeys(features))


def _pipeline(frame: pd.DataFrame, features: list[str], *, alpha: float = 1.0, max_iter: int = 100) -> Pipeline:
    numeric = [name for name in features if pd.api.types.is_numeric_dtype(frame[name])]
    categorical = [name for name in features if name not in numeric]
    transform = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)), ("scale", StandardScaler(with_mean=False))]), numeric),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=100, dtype=np.float64))]), categorical),
    ])
    return Pipeline([("transform", transform), ("model", TweedieRegressor(power=1.5, link="log", alpha=alpha, max_iter=max_iter, tol=1e-5, solver="newton-cholesky"))])


def fit_compact_glm(train: pd.DataFrame, valid: pd.DataFrame, *, line: str, blocks: list[str] | None = None, alpha: float = 1.0, max_iter: int = 100) -> tuple[np.ndarray, Pipeline, dict[str, Any]]:
    blocks = blocks or []
    train_x, features = add_feature_blocks(train, line, blocks)
    valid_x, _ = add_feature_blocks(valid, line, blocks)
    exposure = pd.to_numeric(train["exposure_clean"], errors="coerce").to_numpy(float)
    response = pd.to_numeric(train["observed_net_incurred"], errors="coerce").to_numpy(float)
    if (exposure <= 0).any() or not np.isfinite(exposure).all() or (response < 0).any():
        raise ValueError("invalid exposure or response")
    model = _pipeline(train_x, features, alpha=alpha, max_iter=max_iter)
    start = time.perf_counter()
    model.fit(train_x[features], response / exposure, model__sample_weight=np.sqrt(exposure))
    valid_exposure = valid["exposure_clean"].to_numpy(float)
    prediction = model.predict(valid_x[features]) * valid_exposure
    if not np.isfinite(prediction).all() or (prediction <= 0).any():
        raise ValueError("GLM produced invalid predictions; no clipping applied")
    fitted = model.named_steps["model"]
    return prediction, model, {"features": features, "blocks": blocks, "runtime_seconds": time.perf_counter() - start, "iterations": int(fitted.n_iter_), "converged": bool(fitted.n_iter_ < max_iter)}


def score_vector(actual: np.ndarray, prediction: np.ndarray) -> dict[str, Any]:
    result = metric_report(actual, prediction)
    result.update({"rows": int(len(actual)), "reference_sum": float(actual.sum()), "prediction_sum": float(prediction.sum()), "reference_A_over_E": float(actual.sum() / prediction.sum()), "total_tweedie_deviance": float(result["mean_tweedie_deviance"] * len(actual))})
    return result


def simple_baseline_predictions(train: pd.DataFrame, valid: pd.DataFrame) -> dict[str, np.ndarray]:
    y = train["observed_net_incurred"].to_numpy(float)
    b0 = np.full(len(valid), y.mean())
    rates = train.groupby("line").apply(lambda x: x["observed_net_incurred"].sum() / x["exposure_clean"].sum(), include_groups=False)
    b1 = valid["line"].map(rates).to_numpy(float) * valid["exposure_clean"].to_numpy(float)
    if train["written_premium"].isna().any() or valid["written_premium"].isna().any() or (train["written_premium"] <= 0).any() or (valid["written_premium"] <= 0).any():
        b2 = b1.copy()
        b2_status = "fallback_to_B1_invalid_premium"
    else:
        ratios = train.groupby("line").apply(lambda x: x["observed_net_incurred"].sum() / x["written_premium"].sum(), include_groups=False)
        b2 = valid["line"].map(ratios).to_numpy(float) * valid["written_premium"].to_numpy(float)
        b2_status = "available_conditional_business_comparator"
    return {"B0_global_mean": b0, "B1_line_exposure_rate": b1, "B2_line_premium_ratio": b2, "B2_status": b2_status}
