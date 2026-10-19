"""Run a separate, unpromoted address-feature GLM challenge on frozen folds."""

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
from iaa_hackathon.property_glm import (
    fit_property_glm, join_address_features, load_address_features,
    predict_property_cost, zone_calibration,
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def save_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def line_data(path: Path, line: str, base: dict, address: pd.DataFrame) -> pd.DataFrame:
    columns = {"row_id", "line", "period_start", "period_end", "address_id", "exposure_clean", "observed_net_incurred"}
    columns.update(base["source_features"][line])
    data = pd.read_parquet(path, columns=sorted(columns), filters=[("line", "=", line)]).reset_index(drop=True)
    if len(data) == 0 or not data.line.eq(line).all() or data.row_id.isna().any() or data.row_id.duplicated().any():
        raise ValueError(f"invalid repaired {line} model table")
    return join_address_features(data, address)


def check_membership(fold: str, policy: pd.DataFrame, train_years: list[int], valid_year: int) -> None:
    membership = pd.read_parquet(
        "outputs/step4/folds/fold-membership.parquet",
        columns=["row_id", "fold_id", "role"], filters=[("fold_id", "=", fold)],
    )
    if membership.row_id.duplicated().any() or set(membership.role) != {"train", "validation"}:
        raise ValueError("invalid frozen fold membership")
    policy_ids = set(policy.row_id)
    years = pd.to_datetime(policy.period_start).dt.year
    for role, mask in (("train", years.isin(train_years)), ("validation", years.eq(valid_year))):
        expected = set(policy.loc[mask, "row_id"])
        actual = set(membership.loc[membership.role.eq(role) & membership.row_id.isin(policy_ids), "row_id"])
        if expected != actual or not expected:
            raise ValueError(f"{fold}/{role} does not match frozen membership")


def target_view(fold: str, policy: pd.DataFrame, claims: pd.DataFrame, bridge: dict, target: str) -> pd.DataFrame:
    if target == "observed":
        return policy
    spec = bridge["folds"][fold]
    fitted = read_json(Path(f"outputs/step4/repaired-views/reporting/{fold}-fits.json"))
    if len(fitted) != 15 or any(row["fit_report_cutoff"] != spec["rate_and_delay_cutoff"] or not row["converged"] for row in fitted):
        raise ValueError("reporting fits are not the frozen fold-cutoff fits")
    probabilities = {(row["line"], row["peril"]): float(row["probability"]) for row in fitted if row["line"] == policy.line.iloc[0]}
    line_claims = claims.loc[claims.matched_row_id.isin(policy.row_id)]
    response, _ = bridge_response(
        policy, line_claims, probabilities,
        mature_rate_years=tuple(bridge["mature_rate_years"]),
        rate_cutoff=spec["rate_and_delay_cutoff"],
        valuation_date=bridge["valuation_date"],
    )
    result = policy.copy()
    result["observed_net_incurred"] = response.conditional_ultimate_net_cost.to_numpy(float)
    return result


def saved_baseline(fold: str, line: str, valid: pd.DataFrame, target: str) -> np.ndarray:
    if target == "observed":
        path = Path(f"outputs/step6/features/predictions/{fold}-selected.parquet")
        saved = pd.read_parquet(path, columns=["row_id", "prediction"])
    else:
        path = Path(f"outputs/conditional-ultimate-v1/{fold}-validation.parquet")
        saved = pd.read_parquet(path, columns=["row_id", "conditional_target", "prediction"])
    if saved.row_id.isna().any() or saved.row_id.duplicated().any():
        raise ValueError("saved baseline row identity is invalid")
    merged = valid[["row_id", "observed_net_incurred"]].merge(saved, on="row_id", how="left", validate="one_to_one", sort=False)
    if len(merged) != len(valid) or merged.prediction.isna().any():
        raise ValueError(f"{fold}/{line} baseline coverage is incomplete")
    if target == "conditional" and not np.allclose(merged.observed_net_incurred, merged.conditional_target, atol=1e-7, rtol=0):
        raise ValueError("reconstructed conditional target differs from saved fold response")
    prediction = merged.prediction.to_numpy(float)
    if not np.isfinite(prediction).all() or (prediction <= 0).any():
        raise ValueError("saved baseline has invalid predictions")
    return prediction


def run(data_dir: Path, output_dir: Path, target: str) -> dict:
    if target not in {"observed", "conditional"}:
        raise ValueError("unsupported target")
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing property experiment: {output_dir}")
    base_path = Path("configs/final_model.json")
    base = read_json(base_path)
    config_path = Path("configs/property_feature_challenge.json")
    cfg = read_json(config_path)
    bridge = read_json(Path("configs/conditional_ultimate.json"))
    preflight(base_path, data_dir)
    address_path = data_dir / "addresses.parquet"
    if sha(address_path) != base["raw_sha256"]["addresses.parquet"]:
        raise ValueError("address source identity changed")
    address = load_address_features(address_path)
    claims = None
    if target == "conditional":
        claims = pd.read_parquet(base["claims_path"], columns=[
            "matched_row_id", "line", "peril", "report_date", "accepted_for_observed", "observed_net_incurred",
        ])
    output_dir.mkdir(parents=True)
    rows = []
    with threadpool_limits(limits=base["numerical_threads"]):
        for line in cfg["lines"]:
            data = line_data(Path(base["training_path"]), line, base, address)
            years = pd.to_datetime(data.period_start).dt.year
            if set(years) != set(base["training_years"]):
                raise ValueError(f"{line} training years changed")
            for fold in (cfg["primary_fold"], cfg["challenge_fold"]):
                spec = bridge["folds"][fold]
                check_membership(fold, data, spec["training_years"], spec["validation_year"])
                eligible = years.isin([*spec["training_years"], spec["validation_year"]])
                view = data.loc[eligible].reset_index(drop=True)
                fold_claims = claims.loc[claims.line.eq(line)] if claims is not None else pd.DataFrame()
                view = target_view(fold, view, fold_claims, bridge, target)
                fold_years = pd.to_datetime(view.period_start).dt.year
                train = view.loc[fold_years.isin(spec["training_years"])].reset_index(drop=True)
                valid = view.loc[fold_years.eq(spec["validation_year"])].reset_index(drop=True)
                actual = valid.observed_net_incurred.to_numpy(float)
                baseline = saved_baseline(fold, line, valid, target)
                baseline_score = score_vector(actual, baseline)
                baseline_zones = zone_calibration(valid, actual, baseline)
                case_names = cfg["conditional_cases"] if target == "conditional" else cfg[f"{fold}_cases"]
                for case in case_names:
                    extra = cfg["feature_groups"][case]
                    prediction, model, meta = fit_property_glm(
                        train, valid, line=line, base_blocks=base["blocks"][line], extra_features=extra,
                        alpha=base["settings"]["alpha"], max_iter=base["settings"]["max_iter"],
                    )
                    if not meta["converged"]:
                        raise ValueError(f"{target}/{fold}/{line}/{case} did not converge")
                    model_path = output_dir / "models" / f"{fold}-{line}-{case}.joblib"
                    model_path.parent.mkdir(exist_ok=True)
                    joblib.dump(model, model_path)
                    reloaded = predict_property_cost(
                        joblib.load(model_path), valid, line=line, base_blocks=base["blocks"][line], extra_features=extra,
                    )
                    if not np.array_equal(prediction, reloaded):
                        raise ValueError(f"{target}/{fold}/{line}/{case} reload changed predictions")
                    prediction_path = output_dir / "predictions" / f"{fold}-{line}-{case}.parquet"
                    prediction_path.parent.mkdir(exist_ok=True)
                    pd.DataFrame({"row_id": valid.row_id, "prediction": prediction}).to_parquet(prediction_path, index=False)
                    score = score_vector(actual, prediction)
                    rows.append({
                        "target": target, "fold": fold, "line": line, "candidate": case,
                        "baseline": baseline_score, "candidate_score": score,
                        "delta_mean_deviance": score["mean_tweedie_deviance"] - baseline_score["mean_tweedie_deviance"],
                        "delta_d2": score["d2_tweedie_score"] - baseline_score["d2_tweedie_score"],
                        "baseline_by_flood_zone": baseline_zones,
                        "candidate_by_flood_zone": zone_calibration(valid, actual, prediction),
                        "model_sha256": sha(model_path), "predictions_sha256": sha(prediction_path),
                        **meta,
                    })
                    print(json.dumps({"target": target, "fold": fold, "line": line, "case": case,
                                      "baseline_d2": baseline_score["d2_tweedie_score"], "candidate_d2": score["d2_tweedie_score"],
                                      "delta_deviance": rows[-1]["delta_mean_deviance"]}), flush=True)
    save_json(output_dir / "results.json", {"results": rows})
    summary = {
        "status": "experimental_not_promoted",
        "target": target,
        "config_sha256": sha(config_path),
        "frozen_base_config_sha256": sha(base_path),
        "address_sha256": sha(address_path),
        "repaired_training_sha256": sha(Path(base["training_path"])),
        "rows": len(rows),
        "result_file": "results.json",
        "human_approval": "pending",
        "D2_2025": None,
        "D2_2025_reason": "No 2025 outcome labels are supplied; a D2 cannot be computed from predictions alone.",
    }
    save_json(output_dir / "manifest.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target", choices=["observed", "conditional"], required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.data_dir, args.output_dir, args.target), indent=2))


if __name__ == "__main__":
    main()
