"""Bounded quote-time address-feature challenger; frozen S6 code is unchanged."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from iaa_hackathon.baselines import _pipeline, add_feature_blocks


ADDRESS_COLUMNS = (
    "address_id", "flood_zone", "elevation_m", "distance_to_river_km",
    "bedrooms", "property_type", "year_built",
)
PROPERTY_COLUMNS = ADDRESS_COLUMNS[1:]


def load_address_features(path: Path) -> pd.DataFrame:
    address = pd.read_parquet(path, columns=list(ADDRESS_COLUMNS))
    if address.address_id.isna().any() or address.address_id.duplicated().any():
        raise ValueError("address dimension keys must be non-null and unique")
    flood = pd.to_numeric(address.flood_zone, errors="coerce")
    if ((flood.dropna() % 1 != 0) | ~flood.dropna().between(1, 5)).any():
        raise ValueError("flood_zone must be an integer category from 1 to 5")
    for name in ("elevation_m", "distance_to_river_km", "bedrooms", "year_built"):
        values = pd.to_numeric(address[name], errors="coerce")
        if not np.isfinite(values.dropna().to_numpy(float)).all():
            raise ValueError(f"invalid address field: {name}")
    if (address.elevation_m.dropna() < 0).any() or (address.distance_to_river_km.dropna() < 0).any():
        raise ValueError("negative elevation/distance is outside this experiment contract")
    if (address.bedrooms.dropna() < 0).any() or address.property_type.isna().any():
        raise ValueError("invalid property characteristics")
    return address


def join_address_features(frame: pd.DataFrame, address: pd.DataFrame) -> pd.DataFrame:
    if frame.row_id.isna().any() or frame.row_id.duplicated().any():
        raise ValueError("policy row identity must be unique and non-null")
    if frame.address_id.isna().any() or address.address_id.isna().any() or address.address_id.duplicated().any():
        raise ValueError("address join keys must be complete and many-to-one")
    if any(name in frame.columns for name in PROPERTY_COLUMNS):
        raise ValueError("policy frame already contains address fields")
    result = frame.merge(address[list(ADDRESS_COLUMNS)], on="address_id", how="left", validate="many_to_one", sort=False, indicator=True)
    if len(result) != len(frame) or not np.array_equal(result.row_id.to_numpy(), frame.row_id.to_numpy()):
        raise ValueError("address join changed policy row identity or order")
    if not result._merge.eq("both").all():
        raise ValueError("policy address is absent from dimension")
    result = result.drop(columns="_merge")
    if (pd.to_numeric(result.year_built, errors="coerce") > pd.to_datetime(result.period_start).dt.year).any():
        raise ValueError("a property's year built is after its policy inception")
    flood = pd.to_numeric(result.flood_zone, errors="coerce")
    result["flood_zone"] = flood.map(lambda value: f"zone_{int(value)}" if pd.notna(value) else "missing")
    return result


def fit_property_glm(
    train: pd.DataFrame,
    valid: pd.DataFrame,
    *,
    line: str,
    base_blocks: list[str],
    extra_features: list[str],
    alpha: float,
    max_iter: int,
) -> tuple[np.ndarray, Pipeline, dict[str, Any]]:
    if line not in {"buildings", "contents"} or not extra_features or len(extra_features) != len(set(extra_features)):
        raise ValueError("a unique, non-empty home feature set is required")
    if set(extra_features) - set(PROPERTY_COLUMNS):
        raise ValueError("unapproved address feature")
    if not train.line.eq(line).all() or not valid.line.eq(line).all():
        raise ValueError("line-specific fit received another line")
    train_x, base_features = add_feature_blocks(train, line, base_blocks)
    valid_x, valid_base = add_feature_blocks(valid, line, base_blocks)
    if base_features != valid_base:
        raise ValueError("base feature schema changed")
    features = list(dict.fromkeys([*base_features, *extra_features]))
    if any(name not in train_x or name not in valid_x for name in features):
        raise ValueError("missing model feature")
    exposure = pd.to_numeric(train.exposure_clean, errors="coerce").to_numpy(float)
    response = pd.to_numeric(train.observed_net_incurred, errors="coerce").to_numpy(float)
    valid_exposure = pd.to_numeric(valid.exposure_clean, errors="coerce").to_numpy(float)
    if (not np.isfinite(exposure).all() or (exposure <= 0).any()
            or not np.isfinite(valid_exposure).all() or (valid_exposure <= 0).any()
            or not np.isfinite(response).all() or (response < 0).any()):
        raise ValueError("invalid exposure or training response")
    model = _pipeline(train_x, features, alpha=alpha, max_iter=max_iter)
    start = time.perf_counter()
    model.fit(train_x[features], response / exposure, model__sample_weight=np.sqrt(exposure))
    prediction = model.predict(valid_x[features]) * valid_exposure
    if not np.isfinite(prediction).all() or (prediction <= 0).any():
        raise ValueError("property GLM produced invalid period costs; no clipping applied")
    fitted = model.named_steps["model"]
    return prediction, model, {
        "features": features,
        "base_blocks": base_blocks,
        "extra_features": extra_features,
        "runtime_seconds": time.perf_counter() - start,
        "iterations": int(fitted.n_iter_),
        "converged": bool(fitted.n_iter_ < max_iter),
    }


def predict_property_cost(model: Pipeline, frame: pd.DataFrame, *, line: str, base_blocks: list[str], extra_features: list[str]) -> np.ndarray:
    x, base_features = add_feature_blocks(frame, line, base_blocks)
    features = list(dict.fromkeys([*base_features, *extra_features]))
    if list(model.feature_names_in_) != features:
        raise ValueError("saved property feature schema mismatch")
    prediction = model.predict(x[features]) * frame.exposure_clean.to_numpy(float)
    if not np.isfinite(prediction).all() or (prediction <= 0).any():
        raise ValueError("invalid reloaded property prediction")
    return prediction


def zone_calibration(frame: pd.DataFrame, actual: np.ndarray, prediction: np.ndarray) -> list[dict[str, Any]]:
    if len(frame) != len(actual) or len(frame) != len(prediction):
        raise ValueError("zone calibration arrays are not aligned")
    view = pd.DataFrame({"flood_zone": frame.flood_zone.to_numpy(), "actual": actual, "prediction": prediction})
    if not np.isfinite(view[["actual", "prediction"]].to_numpy(float)).all() or (view.prediction <= 0).any():
        raise ValueError("invalid calibration values")
    grouped = view.groupby("flood_zone", dropna=False, sort=True).agg(rows=("actual", "size"), actual=("actual", "sum"), prediction=("prediction", "sum"))
    return [
        {"flood_zone": str(zone), "rows": int(row.rows), "actual": float(row.actual),
         "prediction": float(row.prediction), "actual_over_expected": float(row.actual / row.prediction)}
        for zone, row in grouped.iterrows()
    ]
