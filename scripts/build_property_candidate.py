"""Build a separate experimental 2025 CSV; never overwrite the frozen candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from iaa_hackathon.conditional_ultimate import bridge_response
from iaa_hackathon.final_submission import preflight, sha, validate_final
from iaa_hackathon.property_glm import (
    fit_property_glm, join_address_features, load_address_features, predict_property_cost,
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def checked_selection(path: Path, challenge_dir: Path, base_path: Path) -> tuple[dict, dict, str]:
    selection = read_json(path)
    if selection["status"] != "experimental_candidate_only_not_final_entry" or selection["selection_fold"] != "F2023":
        raise ValueError("property selection is not the registered primary-fold candidate")
    challenge_path = Path("configs/property_feature_challenge.json")
    manifest = read_json(challenge_dir / "manifest.json")
    if (manifest["status"] != "experimental_not_promoted" or manifest["target"] != "conditional"
            or manifest["config_sha256"] != sha(challenge_path)
            or manifest["frozen_base_config_sha256"] != sha(base_path)):
        raise ValueError("conditional experiment provenance changed")
    results_path = challenge_dir / "results.json"
    results = read_json(results_path)["results"]
    choices = selection["chosen_case_by_line"]
    if choices["motor"] != "unchanged_conditional_ultimate_v1":
        raise ValueError("motor must remain unchanged")
    for line in ("buildings", "contents"):
        case = choices[line]
        for fold in ("F2023", "F2024"):
            matching = [r for r in results if r["line"] == line and r["fold"] == fold and r["candidate"] == case]
            if len(matching) != 1 or not matching[0]["converged"] or matching[0]["delta_mean_deviance"] >= 0:
                raise ValueError(f"selected {line}/{case} did not pass both fold comparisons")
        primary = [r for r in results if r["line"] == line and r["fold"] == "F2023" and r["candidate"] in {"geography_three", "property_three", "all_six"}]
        if min(primary, key=lambda r: r["candidate_score"]["mean_tweedie_deviance"])["candidate"] != case:
            raise ValueError(f"selected {line} case is not primary-fold best among registered groups")
    return selection, read_json(challenge_path), sha(results_path)


def line_table(path: Path, line: str, base: dict, address: pd.DataFrame, *, training: bool) -> pd.DataFrame:
    columns = {"row_id", "line", "period_start", "address_id", "exposure_clean"}
    columns.update(base["source_features"][line])
    if training:
        columns.update({"period_end", "observed_net_incurred"})
    data = pd.read_parquet(path, columns=sorted(columns), filters=[("line", "=", line)]).reset_index(drop=True)
    if data.empty or not data.line.eq(line).all() or data.row_id.isna().any() or data.row_id.duplicated().any():
        raise ValueError(f"invalid {line} policy input")
    expected = set(base["training_years"] if training else [2025])
    if set(pd.to_datetime(data.period_start).dt.year) != expected:
        raise ValueError(f"invalid {line} policy years")
    return join_address_features(data, address)


def run(data_dir: Path, output_dir: Path, csv_dir: Path, challenge_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing candidate: {output_dir}")
    base_path = Path("configs/final_model.json")
    base = read_json(base_path)
    preflight(base_path, data_dir)
    selection_path = Path("configs/property_feature_selection.json")
    selection, challenge, challenge_results_sha = checked_selection(selection_path, challenge_dir, base_path)
    bridge = read_json(Path("configs/conditional_ultimate.json"))
    old_summary = read_json(Path("outputs/conditional-ultimate-v1/summary.json"))
    if old_summary["repaired_policy_sha256"] != sha(Path(base["training_path"])) or old_summary["repaired_claims_sha256"] != sha(Path(base["claims_path"])):
        raise ValueError("original conditional candidate used another claim or policy universe")
    old_csv_path = Path(old_summary["csv_path"])
    if sha(old_csv_path) != old_summary["csv_sha256"]:
        raise ValueError("original conditional CSV changed")
    address_path = data_dir / "addresses.parquet"
    if sha(address_path) != base["raw_sha256"]["addresses.parquet"]:
        raise ValueError("address source identity changed")
    address = load_address_features(address_path)
    claims = pd.read_parquet(base["claims_path"], columns=[
        "matched_row_id", "line", "peril", "report_date", "accepted_for_observed", "observed_net_incurred",
    ])
    probabilities = {(r["line"], r["peril"]): float(r["delay_probability"]) for r in old_summary["full_ibnr_by_peril"]}
    if len(probabilities) != 15:
        raise ValueError("missing full-universe reporting-delay groups")
    output_dir.mkdir(parents=True)
    models_dir = output_dir / "models"
    models_dir.mkdir()
    home_predictions = {}
    line_reports = {}
    with threadpool_limits(limits=base["numerical_threads"]):
        for line in ("buildings", "contents"):
            train = line_table(Path(base["training_path"]), line, base, address, training=True)
            test = line_table(Path(base["test_path"]), line, base, address, training=False)
            claim_line = claims.loc[claims.line.eq(line)]
            response, details = bridge_response(
                train, claim_line,
                {key: value for key, value in probabilities.items() if key[0] == line},
                mature_rate_years=tuple(bridge["mature_rate_years"]),
                rate_cutoff=bridge["full_rate_and_delay_cutoff"],
                valuation_date=bridge["valuation_date"],
            )
            old_ibnr = sum(r["estimated_unreported_cost"] for r in old_summary["full_ibnr_by_peril"] if r["line"] == line)
            if not np.isclose(response.estimated_unreported_net_cost.sum(), old_ibnr, rtol=0, atol=1e-5):
                raise ValueError("full conditional target does not reproduce original IBNR component")
            train["observed_net_incurred"] = response.conditional_ultimate_net_cost.to_numpy(float)
            case = selection["chosen_case_by_line"][line]
            extra = challenge["feature_groups"][case]
            prediction, model, meta = fit_property_glm(
                train, test, line=line, base_blocks=base["blocks"][line], extra_features=extra,
                alpha=base["settings"]["alpha"], max_iter=base["settings"]["max_iter"],
            )
            if not meta["converged"]:
                raise ValueError(f"full {line} property fit failed convergence")
            model_path = models_dir / f"{line}.joblib"
            joblib.dump(model, model_path)
            reloaded = predict_property_cost(joblib.load(model_path), test, line=line, base_blocks=base["blocks"][line], extra_features=extra)
            if not np.array_equal(prediction, reloaded):
                raise ValueError(f"full {line} model reload changed prediction")
            home_predictions[line] = pd.DataFrame({"row_id": test.row_id, "prediction": prediction})
            line_reports[line] = {
                "selected_case": case, "extra_features": extra, "training_rows": len(train), "test_rows": len(test),
                "conditional_training_total": float(train.observed_net_incurred.sum()),
                "estimated_ibnr_total": float(response.estimated_unreported_net_cost.sum()),
                "prediction_total": float(prediction.sum()), "model_sha256": sha(model_path),
                "reproduced_peril_estimates": details, **meta,
            }
    sample = pd.read_parquet(data_dir / base["sample_filename"], columns=["row_id"])
    old = pd.read_csv(old_csv_path, dtype={"row_id": str}, float_precision="round_trip")
    if old.row_id.tolist() != sample.row_id.tolist() or len(old) != base["expected_rows"]:
        raise ValueError("original candidate/sample identity changed")
    full_test = pd.read_parquet(base["test_path"], columns=["row_id", "line", "exposure_clean"])
    expected_old = full_test[["row_id"]].merge(old, on="row_id", how="left", validate="one_to_one", sort=False).prediction.to_numpy(float)
    validate_final(old, sample.row_id.tolist(), full_test, expected_old, base)
    candidate = old.copy()
    for line, replacement in home_predictions.items():
        mask = candidate.row_id.isin(replacement.row_id)
        if int(mask.sum()) != len(replacement) or replacement.row_id.duplicated().any():
            raise ValueError(f"{line} replacement coverage changed")
        candidate.loc[mask, "prediction"] = candidate.loc[mask, "row_id"].map(replacement.set_index("row_id").prediction).to_numpy(float)
    motor = full_test.line.eq("motor")
    old_motor = full_test.loc[motor, "row_id"].to_frame().merge(old, on="row_id", validate="one_to_one", sort=False).prediction.to_numpy(float)
    new_motor = full_test.loc[motor, "row_id"].to_frame().merge(candidate, on="row_id", validate="one_to_one", sort=False).prediction.to_numpy(float)
    if not np.array_equal(old_motor, new_motor):
        raise ValueError("motor predictions changed")
    expected = full_test[["row_id"]].merge(candidate, on="row_id", how="left", validate="one_to_one", sort=False).prediction.to_numpy(float)
    checks = validate_final(candidate, sample.row_id.tolist(), full_test, expected, base)
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_dir / f"part1_conditional_property_{sha(selection_path)[:16]}.csv"
    candidate.to_csv(csv_path, mode="x", index=False, float_format="%.17g", lineterminator="\n", encoding="utf-8")
    reread = pd.read_csv(csv_path, dtype={"row_id": str}, float_precision="round_trip")
    validate_final(reread, sample.row_id.tolist(), full_test, expected, base)
    report = {
        "status": "experimental_not_approved_not_uploaded",
        "selection_sha256": sha(selection_path), "frozen_base_sha256": sha(base_path),
        "conditional_challenge_results_sha256": challenge_results_sha,
        "matches_original_challenge_bytes": challenge_results_sha == selection["conditional_results_sha256"],
        "original_conditional_csv_sha256": old_summary["csv_sha256"],
        "new_csv_path": str(csv_path.resolve()), "new_csv_sha256": sha(csv_path),
        "rows": len(reread), "prediction_total": float(reread.prediction.sum()),
        "original_prediction_total": float(old.prediction.sum()),
        "motor_predictions_unchanged": True, "line_fits": line_reports,
        "csv_checks": checks, "D2_2025": None,
        "D2_2025_reason": "No realised 2025 ultimate claim costs are available.",
        "human_actuarial_approval": "pending",
    }
    with (output_dir / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--csv-dir", type=Path, default=Path("submissions"))
    parser.add_argument("--challenge-dir", type=Path, default=Path("outputs/property-feature-challenge-v1-conditional"))
    args = parser.parse_args()
    report = run(args.data_dir, args.output_dir, args.csv_dir, args.challenge_dir)
    print(json.dumps({key: report[key] for key in ("status", "new_csv_path", "new_csv_sha256", "rows", "prediction_total", "D2_2025")}, indent=2))


if __name__ == "__main__":
    main()
