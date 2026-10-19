"""Fit and audit an assumption-dependent ultimate-cost candidate; never submit it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from iaa_hackathon.baselines import fit_compact_glm, score_vector
from iaa_hackathon.conditional_ultimate import bridge_response
from iaa_hackathon.final_submission import (
    LINES, check_equivalence, data_view, predict_cost, preflight, sha, validate_final,
)
from iaa_hackathon.reporting import fit_reporting_groups


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def save_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def claim_subset(claims: pd.DataFrame, rows: pd.Series) -> pd.DataFrame:
    return claims.loc[claims.matched_row_id.isin(rows)].copy()


def checked_membership(fold: str, frame: pd.DataFrame, train_years: list[int], validation_year: int) -> None:
    membership = pd.read_parquet(
        "outputs/step4/folds/fold-membership.parquet",
        columns=["row_id", "fold_id", "role"], filters=[("fold_id", "=", fold)],
    )
    year = pd.to_datetime(frame.period_start).dt.year
    for role, mask in (("train", year.isin(train_years)), ("validation", year.eq(validation_year))):
        expected = frame.loc[mask, "row_id"]
        actual = membership.loc[membership.role.eq(role), "row_id"]
        if len(expected) != len(actual) or set(expected) != set(actual):
            raise ValueError(f"{fold} {role} is not the frozen membership")


def probabilities_from_saved(fold: str, cutoff: str) -> dict[tuple[str, str], float]:
    records = json.loads(Path(f"outputs/step4/repaired-views/reporting/{fold}-fits.json").read_text())
    if len(records) != 15 or any(r["fit_report_cutoff"] != cutoff or not r["converged"] for r in records):
        raise ValueError(f"{fold} reporting fits are not the frozen cutoff fits")
    return {(r["line"], r["peril"]): float(r["probability"]) for r in records}


def run(*, data_dir: Path, output_dir: Path, csv_dir: Path) -> dict:
    base_path = Path("configs/final_model.json")
    bridge_path = Path("configs/conditional_ultimate.json")
    base, bridge = read_json(base_path), read_json(bridge_path)
    if bridge["case_reserve_multiplier"] != 1 or bridge["future_recovery_allowance"] != 0 or bridge["cost_trend_factor"] != 1:
        raise ValueError("this bridge implements only the declared identity case/recovery/trend assumptions")
    preflight(base_path, data_dir)
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite an existing candidate: {output_dir}")
    output_dir.mkdir(parents=True)
    training, test = data_view(base, training=True), data_view(base, training=False)
    dates = pd.read_parquet(base["training_path"], columns=["row_id", "period_end"])
    if not np.array_equal(training.row_id.to_numpy(), dates.row_id.to_numpy()):
        raise ValueError("period-end view does not match repaired training row order")
    training["period_end"] = dates.period_end.to_numpy()
    claim_columns = ["matched_row_id", "line", "peril", "loss_date", "report_date", "accepted_for_observed", "observed_net_incurred"]
    claims = pd.read_parquet(base["claims_path"], columns=claim_columns)
    if len(training) != base["expected_training_rows"] or len(test) != base["expected_rows"]:
        raise ValueError("repaired policy population changed")
    fold_reports: dict[str, dict] = {}
    with threadpool_limits(limits=base["numerical_threads"]):
        for fold, spec in bridge["folds"].items():
            checked_membership(fold, training, spec["training_years"], spec["validation_year"])
            years = pd.to_datetime(training.period_start).dt.year
            eligible = years.isin([*spec["training_years"], spec["validation_year"]])
            policy_view = training.loc[eligible].reset_index(drop=True)
            claim_view = claim_subset(claims, policy_view.row_id)
            response, details = bridge_response(
                policy_view, claim_view,
                probabilities_from_saved(fold, spec["rate_and_delay_cutoff"]),
                mature_rate_years=tuple(bridge["mature_rate_years"]),
                rate_cutoff=spec["rate_and_delay_cutoff"],
                valuation_date=bridge["valuation_date"],
            )
            fold_years = pd.to_datetime(policy_view.period_start).dt.year
            valid_mask = fold_years.eq(spec["validation_year"]).to_numpy()
            prediction = np.empty(int(valid_mask.sum()), dtype=float)
            validation = policy_view.loc[valid_mask].reset_index(drop=True)
            target = response.loc[valid_mask, "conditional_ultimate_net_cost"].to_numpy(float)
            line_meta = {}
            for line in LINES:
                train_mask = policy_view.line.eq(line).to_numpy() & ~valid_mask
                val_line_mask = validation.line.eq(line).to_numpy()
                tr = policy_view.loc[train_mask].copy()
                tr["observed_net_incurred"] = response.loc[train_mask, "conditional_ultimate_net_cost"].to_numpy(float)
                va = validation.loc[val_line_mask]
                fitted, _, meta = fit_compact_glm(
                    tr, va, line=line, blocks=base["blocks"][line],
                    alpha=base["settings"]["alpha"], max_iter=base["settings"]["max_iter"],
                )
                if not meta["converged"] or meta["features"] != base["features"][line]:
                    raise ValueError(f"{fold}/{line} conditional model did not converge to the frozen feature schema")
                prediction[val_line_mask] = fitted
                line_meta[line] = {"training_rows": len(tr), "validation_rows": len(va), **meta}
            saved = pd.read_parquet(f"outputs/step6/features/predictions/{fold}-selected.parquet", columns=["row_id", "prediction"])
            if len(saved) != len(validation) or set(saved.row_id) != set(validation.row_id):
                raise ValueError(f"{fold} frozen S6 prediction universe changed")
            old = validation[["row_id"]].merge(saved, on="row_id", validate="one_to_one", sort=False).prediction.to_numpy(float)
            fold_reports[fold] = {
                "response_status": "retrospective_conditional_ultimate_not_observed_ultimate",
                "rows": len(validation), "observed_snapshot_total": float(response.loc[valid_mask, "observed_net_incurred"].sum()),
                "estimated_ibnr_total": float(response.loc[valid_mask, "estimated_unreported_net_cost"].sum()),
                "conditional_target_total": float(target.sum()),
                "new_glm_on_conditional_target": score_vector(target, prediction),
                "frozen_s6_on_same_conditional_target": score_vector(target, old),
                "line_fits": line_meta, "ibnr_by_peril": details,
                "financial_vintage_limitation": "All known claim amounts remain valued at end-2024; this is not a prospective ultimate backtest.",
            }
            pd.DataFrame({"row_id": validation.row_id, "fold_id": fold, "conditional_target": target, "prediction": prediction}).to_parquet(output_dir / f"{fold}-validation.parquet", index=False)

        full_fits = fit_reporting_groups(
            claims, cutoff=bridge["full_rate_and_delay_cutoff"],
            estimation_scope="conditional_ultimate_full_repaired_claim_universe",
        )
        full_response, full_details = bridge_response(
            training, claims, {key: fit.probability for key, fit in full_fits.items()},
            mature_rate_years=tuple(bridge["mature_rate_years"]),
            rate_cutoff=bridge["full_rate_and_delay_cutoff"], valuation_date=bridge["valuation_date"],
        )
        models_dir = output_dir / "models"
        models_dir.mkdir()
        full_prediction = np.empty(len(test), dtype=float)
        full_meta = {}
        for line in LINES:
            train_mask = training.line.eq(line).to_numpy()
            test_mask = test.line.eq(line).to_numpy()
            tr = training.loc[train_mask].copy()
            tr["observed_net_incurred"] = full_response.loc[train_mask, "conditional_ultimate_net_cost"].to_numpy(float)
            te = test.loc[test_mask]
            pred, model, meta = fit_compact_glm(
                tr, te, line=line, blocks=base["blocks"][line],
                alpha=base["settings"]["alpha"], max_iter=base["settings"]["max_iter"],
            )
            if not meta["converged"] or meta["features"] != base["features"][line]:
                raise ValueError(f"full/{line} conditional model did not converge to the frozen feature schema")
            model_path = models_dir / f"{line}.joblib"
            joblib.dump(model, model_path)
            check_equivalence(predict_cost(joblib.load(model_path), te, line, base), pred, base["tolerance"])
            full_prediction[test_mask] = pred
            full_meta[line] = {"training_rows": len(tr), "test_rows": len(te), "conditional_target_total": float(tr.observed_net_incurred.sum()), "prediction_total": float(pred.sum()), "model_sha256": sha(model_path), **meta}

    sample = pd.read_parquet(data_dir / base["sample_filename"], columns=["row_id"])
    candidate = sample.merge(test[["row_id"]].assign(prediction=full_prediction), on="row_id", how="left", validate="one_to_one", sort=False)
    checks = validate_final(candidate, sample.row_id.tolist(), test, full_prediction, base)
    csv_dir.mkdir(parents=True, exist_ok=True)
    file_id = hashlib.sha256((sha(bridge_path) + sha(base_path)).encode()).hexdigest()[:16]
    csv_path = csv_dir / f"part1_conditional_ultimate_bf_v1_{file_id}.csv"
    if not csv_path.exists():
        candidate.to_csv(csv_path, mode="x", index=False, float_format="%.17g", lineterminator="\n", encoding="utf-8")
    reread = pd.read_csv(csv_path, dtype={"row_id": str}, float_precision="round_trip")
    validate_final(reread, sample.row_id.tolist(), test, full_prediction, base)
    report = {
        "status": "experimental_not_approved_not_uploaded",
        "config_sha256": sha(bridge_path), "base_model_config_sha256": sha(base_path),
        "repaired_policy_sha256": sha(Path(base["training_path"])), "repaired_claims_sha256": sha(Path(base["claims_path"])),
        "full_observed_snapshot_total": float(full_response.observed_net_incurred.sum()),
        "full_estimated_ibnr_total": float(full_response.estimated_unreported_net_cost.sum()),
        "full_conditional_target_total": float(full_response.conditional_ultimate_net_cost.sum()),
        "full_ibnr_by_peril": full_details,
        "folds": fold_reports, "full_models": full_meta,
        "csv_path": str(csv_path.resolve()), "csv_sha256": sha(csv_path), "csv_rows": len(reread),
        "csv_total": float(reread.prediction.sum()), "csv_mechanical_checks": checks,
        "assumptions": bridge["assumptions"], "limitations": bridge["limitations"],
        "human_actuarial_approval": "pending", "model_promotion": "not_automatic",
    }
    save_json(output_dir / "summary.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/conditional-ultimate-v1"))
    parser.add_argument("--csv-dir", type=Path, default=Path("submissions"))
    args = parser.parse_args()
    result = run(data_dir=args.data_dir, output_dir=args.output_dir, csv_dir=args.csv_dir)
    print(json.dumps({key: result[key] for key in ("status", "full_estimated_ibnr_total", "csv_path", "csv_sha256", "csv_rows", "csv_total")}, indent=2))


if __name__ == "__main__":
    main()
