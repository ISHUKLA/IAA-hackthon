"""Bounded S7 Tweedie challenger with the frozen S6 feature specification."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import time

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_tweedie_deviance

from iaa_hackathon.baselines import add_feature_blocks
from iaa_hackathon.metrics import metric_report


FORBIDDEN = {"row_id", "policy_id", "customer_id", "customer_id_clean", "customer_id_raw", "address_id", "written_premium", "exposure", "exposure_raw", "exposure_clean", "observed_net_incurred", "observed_incurred", "observed_recoveries", "observed_claim_count", "renewal_decision", "customer_service_contacts", "status", "telematics_score", "weather_year", "period_start", "period_end"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_identity(actual: dict, expected: dict) -> None:
    for key, value in expected.items():
        if actual.get(key) != value:
            raise ValueError(f"incompatible provenance: {key}")


def safe_feature_names(names: list[str], allowed: list[str]) -> None:
    if names != allowed or len(names) != len(set(names)):
        raise ValueError("feature names differ from frozen S6 allowlist")
    if FORBIDDEN.intersection(names) or any(name.startswith(("target", "scenario", "observed_", "current_", "claim_")) for name in names):
        raise ValueError("outcome, identifier or timing-unsafe feature")


@dataclass
class FeaturePipeline:
    line: str
    blocks: list[str]
    allowed: list[str]
    vocabularies: dict[str, list[str]] | None = None

    def fit(self, frame: pd.DataFrame) -> "FeaturePipeline":
        derived, names = add_feature_blocks(frame, self.line, self.blocks)
        safe_feature_names(names, self.allowed)
        self.vocabularies = {}
        for name in names:
            if not pd.api.types.is_numeric_dtype(derived[name]):
                self.vocabularies[name] = sorted(derived[name].dropna().astype(str).unique().tolist())
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        if self.vocabularies is None:
            raise ValueError("pipeline is not fitted")
        derived, names = add_feature_blocks(frame, self.line, self.blocks)
        safe_feature_names(names, self.allowed)
        result = derived[names].copy()
        for name in names:
            if name in self.vocabularies:
                # Unknown and missing categories share LightGBM's missing code.
                source = result[name].astype("string")
                result[name] = pd.Categorical(source, categories=self.vocabularies[name])
            else:
                result[name] = pd.to_numeric(result[name], errors="raise").astype(float)
                if np.isinf(result[name]).any():
                    raise ValueError(f"infinite feature: {name}")
        if len(result) != len(frame) or not result.index.equals(frame.index):
            raise ValueError("feature creation changed row identity")
        return result


def exposure_array(frame: pd.DataFrame) -> np.ndarray:
    exposure = frame.exposure_clean.to_numpy(float)
    if not np.isfinite(exposure).all() or (exposure <= 0).any():
        raise ValueError("exposure must be finite and positive")
    return exposure


def rate_response(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    exposure = exposure_array(frame)
    response = frame.observed_net_incurred.to_numpy(float)
    if not np.isfinite(response).all() or (response < 0).any() or response.sum() <= 0:
        raise ValueError("response must be finite, nonnegative and contain positive loss")
    return response / exposure, np.sqrt(exposure)


def period_prediction(model: lgb.Booster, pipeline: FeaturePipeline, frame: pd.DataFrame) -> np.ndarray:
    rate = model.predict(pipeline.transform(frame), num_iteration=model.best_iteration or model.current_iteration(), num_threads=4)
    if not np.isfinite(rate).all() or (rate <= 0).any():
        raise ValueError("invalid rate prediction; no clipping applied")
    result = rate * exposure_array(frame)
    if not np.isfinite(result).all() or (result <= 0).any():
        raise ValueError("invalid period-cost prediction")
    return result


def fit_model(train: pd.DataFrame, validation: pd.DataFrame | None, *, line: str, blocks: list[str], features: list[str], params: dict, rounds: int, early_stopping_rounds: int = 0) -> tuple[lgb.Booster, FeaturePipeline, dict]:
    pipeline = FeaturePipeline(line, blocks, features).fit(train)
    target, weight = rate_response(train)
    matrix = pipeline.transform(train)
    training = lgb.Dataset(matrix, label=target, weight=weight, free_raw_data=True)
    callbacks = []
    history: dict = {}
    kwargs: dict = {}
    if early_stopping_rounds:
        if validation is None:
            raise ValueError("early stopping requires primary-fold validation")
        valid_target, valid_weight = rate_response(validation)
        valid_exposure = exposure_array(validation)
        valid_actual = validation.observed_net_incurred.to_numpy(float)
        held_out = lgb.Dataset(pipeline.transform(validation), label=valid_target, weight=valid_weight, reference=training)

        def period_deviance(rate, dataset):
            return "period_deviance", float(mean_tweedie_deviance(valid_actual, rate * valid_exposure, power=1.5)), False

        kwargs = {"valid_sets": [held_out], "valid_names": ["primary"], "feval": period_deviance}
        callbacks = [lgb.early_stopping(early_stopping_rounds, first_metric_only=True, verbose=False), lgb.record_evaluation(history)]
    started = time.perf_counter()
    model = lgb.train(params, training, num_boost_round=rounds, callbacks=callbacks, **kwargs)
    elapsed = time.perf_counter() - started
    metadata = {"seconds": elapsed, "best_iteration": int(model.best_iteration or model.current_iteration()), "round_cap": rounds, "features": features, "vocabularies": pipeline.vocabularies, "history": history, "matrix_rows": len(matrix), "matrix_columns": len(matrix.columns)}
    return model, pipeline, metadata


def paired_uncertainty(frame: pd.DataFrame, glm: np.ndarray, challenger: np.ndarray, *, seed: int, repeats: int) -> dict:
    y = frame.observed_net_incurred.to_numpy(float)
    def row_deviance(prediction):
        return 4.0 * (y / np.sqrt(prediction) + np.sqrt(prediction) - 2.0 * np.sqrt(y))
    delta = row_deviance(glm) - row_deviance(challenger)
    customer = frame["customer_id_clean"] if "customer_id_clean" in frame else frame.customer_id
    if customer.isna().any():
        raise ValueError("customer cluster key is missing")
    groups = pd.DataFrame({"cluster": customer.to_numpy(), "delta": delta, "rows": 1}).groupby("cluster", sort=True).agg(delta=("delta", "sum"), rows=("rows", "sum"))
    rng = np.random.default_rng(seed)
    sums, counts = groups.delta.to_numpy(), groups.rows.to_numpy()
    samples = []
    for _ in range(repeats):
        indices = rng.integers(0, len(groups), len(groups))
        samples.append(float(sums[indices].sum() / counts[indices].sum()))
    null = float(mean_tweedie_deviance(y, np.full(len(y), y.mean()), power=1.5))
    return {"method": "customer-cluster bootstrap of fixed paired held-out predictions", "clusters": len(groups), "replicates": repeats, "seed": seed, "mean_deviance_gain": float(delta.mean()), "mean_deviance_gain_ci95": np.quantile(samples, [.025, .975]).tolist(), "d2_gain": float(delta.mean() / null), "d2_gain_ci95": (np.quantile(samples, [.025, .975]) / null).tolist(), "independent_temporal_validation": False}


def report_pair(frame: pd.DataFrame, glm: np.ndarray, challenger: np.ndarray) -> dict:
    def summary(part, a, b):
        y = part.observed_net_incurred.to_numpy(float)
        return {"rows": len(part), "exposure": float(part.exposure_clean.sum()), "reference_sum": float(y.sum()), "glm": {**metric_report(y, a), "prediction_sum": float(a.sum()), "A_over_E": float(y.sum() / a.sum()), "predicted_cost_per_exposure": float(a.sum() / part.exposure_clean.sum())}, "lightgbm": {**metric_report(y, b), "prediction_sum": float(b.sum()), "A_over_E": float(y.sum() / b.sum()), "predicted_cost_per_exposure": float(b.sum() / part.exposure_clean.sum())}}
    overall = summary(frame, glm, challenger)
    segments = []
    fields = [name for name in ("line", "new_business", "returning_customer", "returning_policy", "cover_type", "occupancy", "tenure") if name in frame]
    for name in fields:
        for value in frame[name].dropna().unique():
            mask = frame[name].eq(value).to_numpy()
            if mask.sum() < 2:
                continue
            segments.append({"field": name, "value": str(value), **summary(frame.loc[mask], glm[mask], challenger[mask])})
    calibration = []
    for model_name, predicted in (("glm", glm), ("lightgbm", challenger)):
        bands = pd.qcut(pd.Series(predicted).rank(method="first"), 10, labels=False).to_numpy()
        for band in range(10):
            mask = bands == band
            calibration.append({"model": model_name, "prediction_decile": band + 1, "rows": int(mask.sum()), "reference_sum": float(frame.observed_net_incurred.to_numpy()[mask].sum()), "prediction_sum": float(predicted[mask].sum()), "A_over_E": float(frame.observed_net_incurred.to_numpy()[mask].sum() / predicted[mask].sum())})
    tails = []
    y = frame.observed_net_incurred.to_numpy(float)
    for name, mask in (("top_1pct_observed", y >= np.quantile(y, .99)), ("excluding_top_1pct_observed", y < np.quantile(y, .99)), ("top_1pct_predicted", challenger >= np.quantile(challenger, .99))):
        tails.append({"segment": name, **summary(frame.loc[mask], glm[mask], challenger[mask])})
    exposure_bands = pd.cut(frame.exposure_clean, [0, .25, .5, .75, 1, np.inf], include_lowest=True)
    for value in exposure_bands.dropna().unique():
        mask = exposure_bands.eq(value).to_numpy()
        if mask.sum() >= 2:
            segments.append({"field": "exposure_band", "value": str(value), **summary(frame.loc[mask], glm[mask], challenger[mask])})
    return {"overall": overall, "segments": segments, "calibration_by_prediction_decile": calibration, "tails": tails}
