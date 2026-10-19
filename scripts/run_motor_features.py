"""Run the bounded motor NCB/customer/region experiment on frozen folds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from iaa_hackathon.baselines import score_vector
from iaa_hackathon.conditional_ultimate import bridge_response
from iaa_hackathon.final_submission import preflight, sha
from iaa_hackathon.motor_glm import fit_motor_glm, join_motor_features, load_dimensions, predict_motor_cost


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def save_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def check_membership(fold: str, policy: pd.DataFrame, training_years: list[int], validation_year: int) -> None:
    membership = pd.read_parquet(
        "outputs/step4/folds/fold-membership.parquet", columns=["row_id", "fold_id", "role"], filters=[("fold_id", "=", fold)],
    )
    if membership.row_id.isna().any() or membership.row_id.duplicated().any() or set(membership.role) != {"train", "validation"}:
        raise ValueError("invalid frozen fold membership")
    years = pd.to_datetime(policy.period_start).dt.year
    ids = set(policy.row_id)
    for role, mask in (("train", years.isin(training_years)), ("validation", years.eq(validation_year))):
        expected = set(policy.loc[mask, "row_id"])
        actual = set(membership.loc[membership.role.eq(role) & membership.row_id.isin(ids), "row_id"])
        if expected != actual or not expected:
            raise ValueError(f"{fold}/{role} differs from frozen membership")


def conditional_view(policy: pd.DataFrame, claims: pd.DataFrame, bridge: dict, fold: str) -> pd.DataFrame:
    spec = bridge["folds"][fold]
    fitted = read_json(Path(f"outputs/step4/repaired-views/reporting/{fold}-fits.json"))
    if len(fitted) != 15 or any(row["fit_report_cutoff"] != spec["rate_and_delay_cutoff"] or not row["converged"] for row in fitted):
        raise ValueError("reporting fits differ from frozen fold cutoff")
    probabilities = {(row["line"], row["peril"]): float(row["probability"]) for row in fitted if row["line"] == "motor"}
    response, _ = bridge_response(
        policy, claims.loc[claims.matched_row_id.isin(policy.row_id)], probabilities,
        mature_rate_years=tuple(bridge["mature_rate_years"]), rate_cutoff=spec["rate_and_delay_cutoff"],
        valuation_date=bridge["valuation_date"],
    )
    view = policy.copy()
    view["observed_net_incurred"] = response.conditional_ultimate_net_cost.to_numpy(float)
    return view


def saved_baseline(fold: str, valid: pd.DataFrame, target: str) -> np.ndarray:
    path = (Path(f"outputs/step6/features/predictions/{fold}-selected.parquet") if target == "observed"
            else Path(f"outputs/conditional-ultimate-v1/{fold}-validation.parquet"))
    columns = ["row_id", "prediction"] if target == "observed" else ["row_id", "conditional_target", "prediction"]
    saved = pd.read_parquet(path, columns=columns)
    if saved.row_id.isna().any() or saved.row_id.duplicated().any():
        raise ValueError("saved baseline row identity invalid")
    merged = valid[["row_id", "observed_net_incurred"]].merge(saved, on="row_id", how="left", validate="one_to_one", sort=False)
    if len(merged) != len(valid) or merged.prediction.isna().any():
        raise ValueError("saved baseline coverage incomplete")
    if target == "conditional" and not np.allclose(merged.observed_net_incurred, merged.conditional_target, atol=1e-7, rtol=0):
        raise ValueError("conditional target differs from saved response")
    prediction = merged.prediction.to_numpy(float)
    if not np.isfinite(prediction).all() or (prediction <= 0).any():
        raise ValueError("saved baseline prediction invalid")
    return prediction


def score_pair(actual: np.ndarray, prediction: np.ndarray, row_mask: np.ndarray) -> dict:
    return {"all_rows": score_vector(actual, prediction), "without_large_claim_row": score_vector(actual[row_mask], prediction[row_mask])}


def run(data_dir: Path, output_dir: Path, target: str) -> dict:
    if target not in {"observed", "conditional"} or output_dir.exists():
        raise ValueError("invalid target or output directory already exists")
    frozen_path = Path("configs/final_model.json")
    frozen = read_json(frozen_path)
    config_path = Path("configs/motor_feature_challenge.json")
    config = read_json(config_path)
    bridge = read_json(Path("configs/conditional_ultimate.json"))
    preflight(frozen_path, data_dir)
    for filename in ("customers.parquet", "addresses.parquet"):
        if sha(data_dir / filename) != frozen["raw_sha256"][filename]:
            raise ValueError(f"{filename} source identity changed")
    customers, addresses = load_dimensions(data_dir)
    columns = {"row_id", "line", "period_start", "period_end", "exposure_clean", "observed_net_incurred", "customer_id_clean", "address_id",
               "ncb_years", "years_licensed", "ncb_exceeds_licensed_flag"}
    columns.update(frozen["source_features"]["motor"])
    policy = pd.read_parquet(frozen["training_path"], columns=sorted(columns), filters=[("line", "=", "motor")]).reset_index(drop=True)
    if len(policy) != 979968 or policy.row_id.isna().any() or policy.row_id.duplicated().any():
        raise ValueError("repaired motor policy universe differs")
    calculated_flag = policy.ncb_years.gt(policy.years_licensed).fillna(False)
    if not calculated_flag.eq(policy.ncb_exceeds_licensed_flag).all():
        raise ValueError("stored NCB flag differs from ncb_years > years_licensed")
    flag_summary = {"motor_rows": len(policy), "ncb_missing": int(policy.ncb_years.isna().sum()),
                    "ncb_exceeds_licensed_rows": int(calculated_flag.sum())}
    policy = join_motor_features(policy, customers, addresses)
    claims = pd.read_parquet(frozen["claims_path"], columns=[
        "claim_id", "matched_row_id", "line", "peril", "loss_date", "report_date", "accepted_for_observed", "observed_net_incurred",
    ])
    accepted = claims.loc[claims.accepted_for_observed & claims.matched_row_id.notna()]
    large = accepted.loc[accepted.observed_net_incurred.idxmax()]
    if large.line != "motor" or large.peril != "bodily_injury" or pd.Timestamp(large.loss_date).year != 2023 or not 11_890_000 < large.observed_net_incurred < 11_900_000:
        raise ValueError("the documented 11.89M accepted motor claim was not found")
    large_row_id = large.matched_row_id
    output_dir.mkdir(parents=True)
    results = []
    with threadpool_limits(limits=frozen["numerical_threads"]):
        for fold in (config["primary_fold"], config["challenge_fold"]):
            spec = bridge["folds"][fold]
            check_membership(fold, policy, spec["training_years"], spec["validation_year"])
            years = pd.to_datetime(policy.period_start).dt.year
            view = policy.loc[years.isin([*spec["training_years"], spec["validation_year"]])].reset_index(drop=True)
            if target == "conditional":
                view = conditional_view(view, claims.loc[claims.line.eq("motor")], bridge, fold)
            view_years = pd.to_datetime(view.period_start).dt.year
            train = view.loc[view_years.isin(spec["training_years"])].reset_index(drop=True)
            valid = view.loc[view_years.eq(spec["validation_year"])].reset_index(drop=True)
            actual = valid.observed_net_incurred.to_numpy(float)
            keep = ~valid.row_id.eq(large_row_id).to_numpy()
            if (fold == "F2023" and int((~keep).sum()) != 1) or (fold == "F2024" and not keep.all()):
                raise ValueError("large-claim row appears in unexpected validation fold")
            baseline = saved_baseline(fold, valid, target)
            baseline_scores = score_pair(actual, baseline, keep)
            for case, definition in config["cases"].items():
                prediction, model, metadata = fit_motor_glm(
                    train, valid, mode=definition["mode"], extras=definition["extras"],
                    blocks=[] if definition["mode"] == "univariate" else frozen["blocks"]["motor"],
                    alpha=frozen["settings"]["alpha"], max_iter=frozen["settings"]["max_iter"],
                )
                if not metadata["converged"]:
                    raise ValueError(f"{fold}/{case} did not converge")
                model_path = output_dir / "models" / f"{fold}-{case}.joblib"
                model_path.parent.mkdir(exist_ok=True)
                joblib.dump(model, model_path)
                reloaded = predict_motor_cost(joblib.load(model_path), valid, mode=definition["mode"],
                                              extras=definition["extras"], blocks=metadata["blocks"])
                if not np.array_equal(prediction, reloaded):
                    raise ValueError(f"{fold}/{case} reload changed predictions")
                prediction_path = output_dir / "predictions" / f"{fold}-{case}.parquet"
                prediction_path.parent.mkdir(exist_ok=True)
                pd.DataFrame({"row_id": valid.row_id, "prediction": prediction}).to_parquet(prediction_path, index=False)
                scores = score_pair(actual, prediction, keep)
                flag = valid.ncb_exceeds_licensed_flag.to_numpy(bool)
                results.append({"target": target, "fold": fold, "case": case, "train_rows": len(train), "valid_rows": len(valid),
                                "baseline": baseline_scores, "candidate": scores,
                                "flagged_validation_rows": int(flag.sum()),
                                "flagged_A_over_E": float(actual[flag].sum() / prediction[flag].sum()),
                                "unflagged_A_over_E": float(actual[~flag].sum() / prediction[~flag].sum()),
                                "model_sha256": sha(model_path), "predictions_sha256": sha(prediction_path), **metadata})
                print(json.dumps({"target": target, "fold": fold, "case": case,
                                  "D2": scores["all_rows"]["d2_tweedie_score"],
                                  "D2_without_row": scores["without_large_claim_row"]["d2_tweedie_score"]}), flush=True)
    save_json(output_dir / "results.json", {"source_flag_summary": flag_summary,
                                            "large_claim_amount": float(large.observed_net_incurred), "large_claim_row_id": large_row_id,
                                            "results": results})
    manifest = {"status": "experimental_not_promoted", "target": target, "cases": len(results),
                "config_sha256": sha(config_path), "frozen_config_sha256": sha(frozen_path),
                "repaired_training_sha256": sha(Path(frozen["training_path"])),
                "customer_sha256": sha(data_dir / "customers.parquet"), "address_sha256": sha(data_dir / "addresses.parquet"),
                "human_approval": "pending", "D2_2025": None,
                "D2_2025_reason": "No 2025 ultimate outcomes are supplied; fold scores are retrospective and target-dependent."}
    save_json(output_dir / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target", choices=["observed", "conditional"], required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.data_dir, args.output_dir, args.target), indent=2))


if __name__ == "__main__":
    main()
