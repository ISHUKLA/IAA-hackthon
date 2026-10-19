"""Unpromoted motor feature challenger; frozen S6 implementation is unchanged."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from iaa_hackathon.baselines import _pipeline, add_feature_blocks


CUSTOMER_FIELDS = ("marital_status", "occupation", "prior_claims_5y")
ADDRESS_FIELDS = ("region",)
EXTRA_FIELDS = ("ncb_years", *CUSTOMER_FIELDS, *ADDRESS_FIELDS)


def load_dimensions(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = pd.read_parquet(data_dir / "customers.parquet", columns=["customer_id", *CUSTOMER_FIELDS])
    addresses = pd.read_parquet(data_dir / "addresses.parquet", columns=["address_id", *ADDRESS_FIELDS])
    for name, dimension, key in (("customers", customers, "customer_id"), ("addresses", addresses, "address_id")):
        if dimension[key].isna().any() or dimension[key].duplicated().any():
            raise ValueError(f"{name} dimension does not have unique complete keys")
    if addresses.region.isna().any():
        raise ValueError("region is missing in the address dimension")
    if (customers.prior_claims_5y.dropna() < 0).any():
        raise ValueError("negative prior_claims_5y")
    return customers, addresses


def join_motor_features(frame: pd.DataFrame, customers: pd.DataFrame, addresses: pd.DataFrame) -> pd.DataFrame:
    if frame.row_id.isna().any() or frame.row_id.duplicated().any():
        raise ValueError("motor policy row identity is invalid")
    if not frame.line.eq("motor").all() or frame.customer_id_clean.isna().any() or frame.address_id.isna().any():
        raise ValueError("motor policy line or dimension keys are invalid")
    if any(name in frame for name in (*CUSTOMER_FIELDS, *ADDRESS_FIELDS)):
        raise ValueError("motor feature already present before dimension join")
    result = frame.merge(customers, left_on="customer_id_clean", right_on="customer_id", how="left", validate="many_to_one", sort=False, indicator=True)
    if not result._merge.eq("both").all():
        raise ValueError("unmatched motor customer")
    result = result.drop(columns=["customer_id", "_merge"])
    result = result.merge(addresses, on="address_id", how="left", validate="many_to_one", sort=False, indicator=True)
    if not result._merge.eq("both").all() or len(result) != len(frame) or not np.array_equal(result.row_id.to_numpy(), frame.row_id.to_numpy()):
        raise ValueError("motor dimension join lost, multiplied or reordered rows")
    result = result.drop(columns="_merge")
    for field in ("marital_status", "occupation", "region"):
        result[field] = result[field].astype(object).where(result[field].notna(), np.nan)
    return result


def model_features(frame: pd.DataFrame, *, mode: str, extras: list[str], blocks: list[str]) -> tuple[pd.DataFrame, list[str]]:
    allowed = set(EXTRA_FIELDS) | ({"driver_age"} if mode == "univariate" else set())
    if len(extras) != len(set(extras)) or set(extras) - allowed:
        raise ValueError("unapproved or duplicate motor feature")
    if mode == "univariate":
        if blocks or len(extras) != 1 or extras[0] not in {"ncb_years", "driver_age"}:
            raise ValueError("univariate motor probe requires one age/NCB feature")
        return frame.copy(), extras
    if mode != "s6" or "ncb_years" not in extras:
        raise ValueError("S6 motor challenger must include NCB")
    result, features = add_feature_blocks(frame, "motor", blocks)
    return result, list(dict.fromkeys([*features, *extras]))


def fit_motor_glm(
    train: pd.DataFrame, valid: pd.DataFrame, *, mode: str, extras: list[str], blocks: list[str], alpha: float, max_iter: int,
) -> tuple[np.ndarray, Pipeline, dict[str, Any]]:
    if not train.line.eq("motor").all() or not valid.line.eq("motor").all():
        raise ValueError("motor fit received another line")
    train_x, features = model_features(train, mode=mode, extras=extras, blocks=blocks)
    valid_x, valid_features = model_features(valid, mode=mode, extras=extras, blocks=blocks)
    if features != valid_features or any(name not in train_x or name not in valid_x for name in features):
        raise ValueError("motor feature schema differs between train and validation")
    exposure = pd.to_numeric(train.exposure_clean, errors="coerce").to_numpy(float)
    valid_exposure = pd.to_numeric(valid.exposure_clean, errors="coerce").to_numpy(float)
    response = pd.to_numeric(train.observed_net_incurred, errors="coerce").to_numpy(float)
    if (not np.isfinite(exposure).all() or (exposure <= 0).any() or not np.isfinite(valid_exposure).all()
            or (valid_exposure <= 0).any() or not np.isfinite(response).all() or (response < 0).any()):
        raise ValueError("invalid motor exposure or response")
    model = _pipeline(train_x, features, alpha=alpha, max_iter=max_iter)
    start = time.perf_counter()
    model.fit(train_x[features], response / exposure, model__sample_weight=np.sqrt(exposure))
    prediction = model.predict(valid_x[features]) * valid_exposure
    if not np.isfinite(prediction).all() or (prediction <= 0).any():
        raise ValueError("invalid motor period-cost prediction; no clipping applied")
    fitted = model.named_steps["model"]
    return prediction, model, {
        "features": features, "mode": mode, "extras": extras, "blocks": blocks,
        "runtime_seconds": time.perf_counter() - start,
        "iterations": int(fitted.n_iter_), "converged": bool(fitted.n_iter_ < max_iter),
    }


def predict_motor_cost(model: Pipeline, frame: pd.DataFrame, *, mode: str, extras: list[str], blocks: list[str]) -> np.ndarray:
    data, features = model_features(frame, mode=mode, extras=extras, blocks=blocks)
    if list(model.feature_names_in_) != features:
        raise ValueError("reloaded motor feature schema mismatch")
    prediction = model.predict(data[features]) * frame.exposure_clean.to_numpy(float)
    if not np.isfinite(prediction).all() or (prediction <= 0).any():
        raise ValueError("invalid reloaded motor prediction")
    return prediction
