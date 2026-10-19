"""One S8 contents curvature term; all S6 predictors/settings remain fixed."""
from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np
import pandas as pd

from iaa_hackathon.baselines import _pipeline, add_feature_blocks
from iaa_hackathon.lightgbm_challenger import exposure_array, rate_response, safe_feature_names


FEATURE = "contents_insured_tent"


def insured_tent(insured: pd.Series, knots: list[float]) -> np.ndarray:
    """Training-quantile tent in log-insured units; missing adds neutral zero."""
    values = pd.to_numeric(insured, errors="raise").to_numpy(float)
    if (values[np.isfinite(values)] < 0).any() or np.isinf(values).any():
        raise ValueError("sum insured must be nonnegative and finite or missing")
    if len(knots) != 3 or not np.isfinite(knots).all() or not knots[0] < knots[1] < knots[2]:
        raise ValueError("tent knots must be three strictly increasing finite values")
    lower, middle, upper = knots
    logged = np.log1p(values)
    tent = np.maximum(0.0, np.minimum((logged - lower) / (middle - lower), (upper - logged) / (upper - middle)))
    # This is a feature basis, not a floor or cap on predictions or responses.
    return np.where(np.isnan(values), 0.0, tent)


@dataclass
class ContentsRefinement:
    blocks: list[str]
    source_features: list[str]
    alpha: float = 1.0
    max_iter: int = 100
    knots: list[float] | None = None
    model: object = None
    metadata: dict | None = None

    def matrix(self, frame: pd.DataFrame) -> pd.DataFrame:
        if self.knots is None:
            raise ValueError("refinement has not learned training knots")
        derived, names = add_feature_blocks(frame, "contents", self.blocks)
        safe_feature_names(names, self.source_features)
        matrix = derived[names].copy()
        matrix[FEATURE] = insured_tent(frame.sum_insured_repaired, self.knots)
        if not matrix.index.equals(frame.index):
            raise ValueError("feature construction changed row identity")
        return matrix

    def fit(self, training: pd.DataFrame) -> "ContentsRefinement":
        target, weight = rate_response(training)
        values = pd.to_numeric(training.sum_insured_repaired, errors="raise").dropna().to_numpy(float)
        if len(values) < 3 or (values < 0).any() or not np.isfinite(values).all():
            raise ValueError("insufficient valid training insured values")
        self.knots = np.quantile(np.log1p(values), [.2, .5, .8]).tolist()
        matrix = self.matrix(training)
        names = [*self.source_features, FEATURE]
        self.model = _pipeline(matrix, names, alpha=self.alpha, max_iter=self.max_iter)
        started = time.perf_counter()
        self.model.fit(matrix, target, model__sample_weight=weight)
        iterations = int(self.model.named_steps["model"].n_iter_)
        if iterations >= self.max_iter:
            raise ValueError("restricted GLM did not converge")
        transformed_names = self.model.named_steps["transform"].get_feature_names_out().tolist()
        self.metadata = {"fit_seconds": time.perf_counter() - started, "iterations": iterations, "converged": True, "knots_log_insured": self.knots, "input_features": names, "transformed_features": transformed_names, "additional_numeric_basis_columns": 1, "tent_coefficient": float(self.model.named_steps["model"].coef_[transformed_names.index(f"numeric__{FEATURE}")])}
        return self

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("refinement is not fitted")
        rate = self.model.predict(self.matrix(frame))
        result = rate * exposure_array(frame)
        if not np.isfinite(result).all() or (result <= 0).any():
            raise ValueError("invalid prediction; no clipping applied")
        return result


def promotion_decision(gates: dict[str, dict]) -> str:
    if set(gates) != {str(number) for number in range(1, 8)}:
        raise ValueError("all seven promotion gates must be reported")
    if any(gate.get("status") == "blocked" for gate in gates.values()):
        return "blocked"
    if all(gate.get("status") == "pass" for gate in gates.values()):
        return "promote_candidate"
    return "retain_benchmark"
