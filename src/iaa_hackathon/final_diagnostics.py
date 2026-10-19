"""Aggregate-only financial review; none of these diagnostics changes the CSV."""
from __future__ import annotations

from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from iaa_hackathon.final_submission import LINES, data_view, model_predictions, predict_cost, read_json, save_json


def distribution(frame: pd.DataFrame, prediction: np.ndarray, cfg: dict) -> dict:
    result = {}
    for line in LINES:
        mask = frame.line.eq(line).to_numpy()
        p = prediction[mask]
        exposure = float(frame.loc[mask, "exposure_clean"].sum())
        small, large = p < cfg["diagnostics"]["small_cost"], p > cfg["diagnostics"]["large_cost"]
        result[line] = {"rows": len(p), "exposure": exposure, "prediction_total": float(p.sum()), "cost_per_exposure": float(p.sum() / exposure), "quantiles": {str(q): float(np.quantile(p, q)) for q in (0, .01, .05, .5, .9, .95, .99, .999, 1)}, "small_count": int(small.sum()), "small_total": float(p[small].sum()), "large_count": int(large.sum()), "large_total": float(p[large].sum())}
    result["overall"] = {"rows": len(frame), "exposure": float(frame.exposure_clean.sum()), "prediction_total": float(prediction.sum()), "cost_per_exposure": float(prediction.sum() / frame.exposure_clean.sum())}
    return result


def diagnostics(cfg: dict, output: Path) -> dict:
    train, test = data_view(cfg, training=True), data_view(cfg, training=False)
    with threadpool_limits(limits=cfg["numerical_threads"]):
        pred = model_predictions(cfg, output, test)
        insample = model_predictions(cfg, output, train)
        prior = np.empty(len(test), float)
        for line in LINES:
            mask = test.line.eq(line).to_numpy()
            model = joblib.load(f"outputs/step6/features/models/F2024-{line}-selected.joblib")
            prior[mask] = predict_cost(model, test.loc[mask], line, cfg)
    stats = distribution(test, pred, cfg)
    full_train = distribution(train, insample, cfg)
    cohort = train.assign(year=pd.to_datetime(train.period_start).dt.year).groupby(["line", "year"]).agg(rows=("row_id", "size"), exposure=("exposure_clean", "sum"), observed=("observed_net_incurred", "sum"))
    cohort["observed_per_exposure"] = cohort.observed / cohort.exposure
    cohort_rows = cohort.reset_index().to_dict("records")
    alerts, refit = [], {}
    for line in LINES:
        mask = test.line.eq(line).to_numpy()
        ratio = pred[mask] / prior[mask]
        change = float(pred[mask].sum() / prior[mask].sum() - 1)
        refit[line] = {"fold_F2024_model_on_same_2025_rows_total": float(prior[mask].sum()), "full_model_on_same_2025_rows_total": float(pred[mask].sum()), "total_change_fraction": change, "row_ratio_min": float(ratio.min()), "row_ratio_max": float(ratio.max()), "ratio_quantiles": {str(q): float(np.quantile(ratio, q)) for q in (.01, .5, .99)}}
        if abs(change) > cfg["diagnostics"]["refit_total_alert_fraction"]:
            alerts.append({"severity": "review", "line": line, "issue": "material full-refit shift", "explanation": "Compare year/line observed rates below: adding immature 2024 changes the fitted snapshot reference. No recalibration applied; human review required."})
        full_train[line]["observed_total"] = float(train.loc[train.line.eq(line), "observed_net_incurred"].sum())
        full_train[line]["in_sample_A_over_E"] = full_train[line]["observed_total"] / full_train[line]["prediction_total"]
    segments = []
    for key in ("policy_id", "customer_id_clean"):
        returning = test[key].isin(set(train[key])).to_numpy()
        for line in LINES:
            for status, flag in (("returning", returning), ("new", ~returning)):
                mask = flag & test.line.eq(line).to_numpy()
                segments.append({"entity": key, "line": line, "segment": status, "rows": int(mask.sum()), "exposure": float(test.loc[mask, "exposure_clean"].sum()), "prediction_total": float(pred[mask].sum()), "predicted_cost_per_exposure": float(pred[mask].sum() / test.loc[mask, "exposure_clean"].sum()) if mask.any() else None})
    # Only a diagnostic counterfactual: keep the fitted model fixed and switch
    # the SI input to preserved raw units, never refit or adopt its predictions.
    si_sensitivity = {}
    with threadpool_limits(limits=cfg["numerical_threads"]):
        for line in ("buildings", "contents"):
            mask = test.line.eq(line).to_numpy()
            alternative = test.loc[mask].copy()
            changed = alternative.sum_insured_repaired_flag.fillna(False).to_numpy(bool)
            alternative["sum_insured_repaired"] = alternative.sum_insured_raw
            model = joblib.load(output / "models" / f"{line}.joblib")
            entry = {"affected_test_rows": int(changed.sum()), "chosen_candidate_affected_prediction_total": float(pred[mask][changed].sum()), "interpretation": "raw-unit counterfactual only; no model/response selection, no adoption"}
            try:
                with warnings.catch_warnings(), np.errstate(over="ignore", invalid="ignore"):
                    warnings.simplefilter("ignore", RuntimeWarning)
                    raw_pred = predict_cost(model, alternative, line, cfg)
                total = float(raw_pred.sum())
                if not np.isfinite(total):
                    raise ValueError("non-finite raw-unit aggregate")
                entry.update({"raw_unit_counterfactual_total": total, "difference_from_selected_total": total - float(pred[mask].sum())})
            except ValueError as exc:
                entry.update({"raw_unit_counterfactual_total": None, "status": "not_quantifiable_with_finite_predictions", "reason": str(exc)})
            si_sensitivity[line] = entry
    claims = pd.read_parquet(cfg["claims_path"], columns=["accepted_for_observed", "case_reserve", "recoveries", "observed_net_incurred"])
    accepted = claims[claims.accepted_for_observed]
    reserve = float(accepted.case_reserve.sum())
    observed = float(train.observed_net_incurred.sum())
    sensitivity = {"recorded_recoveries_subtracted_from_training_reference": float(accepted.recoveries.sum()), "already_net_incurred_interpretation_adds_to_training_reference": float(accepted.recoveries.sum()), "case_balance": reserve, "illustrative_case_0p8_training_reference": observed - .2 * reserve, "illustrative_case_1p2_training_reference": observed + .2 * reserve, "no_refitted_predictions_for_alternative_responses": True, "chosen_unreported_loss_allowance": 0, "chosen_further_development_adjustment": 0, "chosen_future_recovery_adjustment": 0, "chosen_2025_trend_factor": 1, "reason": "identity snapshot proxy, not estimates that these ultimate components are zero", "additional_adjustment_to_final_predictions": 0, "ultimate_prediction_sensitivity": "not identified: no supported monetary IBNR, reserve adequacy, future recovery or trend parameters; do not invent a quantitative bound"}
    # Earlier calibrated holdout evidence remains separate from unlabelled 2025.
    inherited = {fold: value["benchmark"] for fold, value in read_json(Path("outputs/step8/decision.json"))["folds"].items()}
    result = {"status": "complete", "no_test_outcomes_used": True, "test": stats, "full_training_in_sample_not_validation": full_train, "training_observed_by_line_year": cohort_rows, "full_training_observed_total": observed, "training_raw_vs_clean_exposure": {"raw": float(train.exposure_raw.sum()), "clean": float(train.exposure_clean.sum()), "test_exposure_unchanged_from_sources": True}, "same_test_rows_full_refit_vs_F2024_model": refit, "inherited_validation_not_test_calibration": inherited, "new_returning": segments, "sum_insured_fixed_model_sensitivity": si_sensitivity, "financial_basis_sensitivity": sensitivity, "alerts": alerts, "unexplained_critical_alerts": [], "human_review": "pending"}
    save_json(output / "financial-diagnostics.json", result)
    return result


def diagnostic_markdown(result: dict) -> str:
    text = "# Step 9 submission diagnostics\n\nThese are snapshot-proxy predictions, not validated ultimate outcomes. No 2025 labels exist. All totals are CU; exposure uses the inherited ACT/365 candidate. No total was forced, clipped or recalibrated.\n\n"
    text += "## 2025 predictions\n\n| Line | Rows | Exposure | Total CU | Cost/exposure | Small <1 count/total | Large >10000 count/total |\n| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n"
    for line in LINES:
        x = result["test"][line]
        text += f"| {line} | {x['rows']} | {x['exposure']:.4f} | {x['prediction_total']:.2f} | {x['cost_per_exposure']:.6f} | {x['small_count']} / {x['small_total']:.2f} | {x['large_count']} / {x['large_total']:.2f} |\n"
    overall = result["test"]["overall"]
    text += f"\nOverall: {overall['rows']:,} rows, {overall['exposure']:.4f} exposure, {overall['prediction_total']:.2f} CU, {overall['cost_per_exposure']:.6f} CU/exposure. Quantiles below are row costs, not rates.\n\n"
    for key, title in (("test", "Full distribution"), ("full_training_in_sample_not_validation", "Full-training comparison (in-sample, not validation)"), ("training_observed_by_line_year", "Observed snapshot cohort rates"), ("same_test_rows_full_refit_vs_F2024_model", "Controlled same-2025-row full-refit distribution comparison"), ("inherited_validation_not_test_calibration", "Inherited holdout calibration — NOT test calibration"), ("new_returning", "Returning/new policies and customers"), ("sum_insured_fixed_model_sensitivity", "Unresolved sum-insured unit sensitivity"), ("financial_basis_sensitivity", "Maturity, recovery and trend sensitivity"), ("alerts", "Review alerts")):
        import json
        text += f"## {title}\n\n```json\n{json.dumps(result[key], indent=2, allow_nan=False)}\n```\n\n"
    text += "## Interpretation and limitations\n\nFull refitting adds the immature 2024 snapshot. Earlier monetary labels were valued at end-2024, not at historical prediction boundaries; comparisons remain retrospective proxies. F2024 was reused during development. The primary F2023 S6 A/E is 1.049931; F2024 is 0.908890, especially motor 0.803431. These are material maturity/calibration limitations, not evidence to scale 2025 totals. The 11.89m CU BI claim was retained.\n\nRaw SI sensitivity deliberately extrapolates values believed to have a unit error; even a finite huge counterfactual is not a plausible alternative forecast. Its impact motivates human review of the 730 repaired test values, not a model change in Step 9. Recovery interpretation and case stresses quantify uncertainty in the repaired TRAINING reference only; they do not imply a matching change in model predictions without a separately authorised refit. The ultimate effect of unreported/developing claims and 2025 trend cannot be quantified from this snapshot alone. Zero added allowances mean a proxy specification, not actuarial estimates of zero uncertainty. Quarantined claims remain excluded.\n\nNo unexplained critical mechanical/distribution alert remains if the acceptance gate passes; disclosed financial uncertainties remain unresolved. No actuarial approval, official scorer equivalence, Kaggle acceptance or production readiness is claimed. Current Kaggle access failed; old deadlines and submission limits are not reverified. Human review and final Kaggle-entry selection remain pending.\n"
    return text
