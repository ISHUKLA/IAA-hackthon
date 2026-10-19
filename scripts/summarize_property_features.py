"""Score full held-out folds after replacing home predictions only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from iaa_hackathon.baselines import score_vector


CASES = ("geography_three", "property_three", "all_six")
FOLDS = {"F2023": 2023, "F2024": 2024}
LINES = ("buildings", "contents")


def run(output_dir: Path, *, selected: bool = False) -> dict:
    manifest = json.loads((output_dir / "manifest.json").read_text())
    if manifest["status"] != "experimental_not_promoted":
        raise ValueError("incomplete property experiment")
    target = manifest["target"]
    base = json.loads(Path("configs/final_model.json").read_text())
    if target not in {"observed", "conditional"}:
        raise ValueError("unsupported target")
    policy = pd.read_parquet(base["training_path"], columns=["row_id", "line", "period_start", "observed_net_incurred"])
    if policy.row_id.isna().any() or policy.row_id.duplicated().any():
        raise ValueError("invalid repaired policy identity")
    years = pd.to_datetime(policy.period_start).dt.year
    selection = json.loads(Path("configs/property_feature_selection.json").read_text()) if selected else None
    if selection is not None:
        from iaa_hackathon.final_submission import sha
        challenge = Path("configs/property_feature_challenge.json")
        if manifest["config_sha256"] != sha(challenge) or selection["target"] != "conditional_ultimate_bf_v1_assumption_dependent":
            raise ValueError("selected property experiment configuration changed")
        rows = json.loads((output_dir / "results.json").read_text())["results"]
        for line in LINES:
            case = selection["chosen_case_by_line"][line]
            matching = [r for r in rows if r["line"] == line and r["fold"] == "F2023" and r["candidate"] == case]
            if len(matching) != 1 or matching[0]["delta_mean_deviance"] >= 0:
                raise ValueError("selected feature group does not improve its primary-fold line")
    results = []
    for fold, year in FOLDS.items():
        valid = policy.loc[years.eq(year), ["row_id", "line", "observed_net_incurred"]].reset_index(drop=True)
        if target == "observed":
            saved = pd.read_parquet(f"outputs/step6/features/predictions/{fold}-selected.parquet", columns=["row_id", "prediction"])
        else:
            saved = pd.read_parquet(f"outputs/conditional-ultimate-v1/{fold}-validation.parquet", columns=["row_id", "conditional_target", "prediction"])
        if saved.row_id.isna().any() or saved.row_id.duplicated().any() or len(saved) != len(valid) or set(saved.row_id) != set(valid.row_id):
            raise ValueError(f"{fold} baseline does not cover the held-out rows exactly")
        valid = valid.merge(saved, on="row_id", how="left", validate="one_to_one", sort=False)
        actual = valid["conditional_target" if target == "conditional" else "observed_net_incurred"].to_numpy(float)
        baseline = valid.prediction.to_numpy(float)
        if not np.isfinite(baseline).all() or (baseline <= 0).any():
            raise ValueError("invalid frozen baseline")
        base_score = score_vector(actual, baseline)
        for case in (("selected_primary",) if selected else CASES):
            candidate = baseline.copy()
            for line in LINES:
                mask = valid.line.eq(line).to_numpy()
                line_case = selection["chosen_case_by_line"][line] if selection is not None else case
                file = output_dir / "predictions" / f"{fold}-{line}-{line_case}.parquet"
                saved_line = pd.read_parquet(file, columns=["row_id", "prediction"])
                line_ids = valid.loc[mask, "row_id"]
                if saved_line.row_id.isna().any() or saved_line.row_id.duplicated().any() or len(saved_line) != len(line_ids) or set(saved_line.row_id) != set(line_ids):
                    raise ValueError(f"{fold}/{line}/{case} coverage changed")
                aligned = line_ids.to_frame().merge(saved_line, on="row_id", how="left", validate="one_to_one", sort=False)
                candidate[mask] = aligned.prediction.to_numpy(float)
            if not np.array_equal(candidate[valid.line.eq("motor").to_numpy()], baseline[valid.line.eq("motor").to_numpy()]):
                raise ValueError("motor predictions changed")
            score = score_vector(actual, candidate)
            results.append({
                "target": target, "fold": fold, "candidate": case,
                "baseline": base_score, "candidate_score": score,
                "delta_mean_deviance": score["mean_tweedie_deviance"] - base_score["mean_tweedie_deviance"],
                "delta_d2": score["d2_tweedie_score"] - base_score["d2_tweedie_score"],
                "motor_predictions_unchanged": True,
            })
    report = {"status": "complete", "target": target, "rows": results, "D2_2025": None}
    with (output_dir / ("aggregate-selected.json" if selected else "aggregate.json")).open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--selected", action="store_true")
    args = parser.parse_args()
    report = run(args.output_dir, selected=args.selected)
    for row in report["rows"]:
        print(json.dumps({key: row[key] for key in ("target", "fold", "candidate", "delta_mean_deviance", "delta_d2")}))


if __name__ == "__main__":
    main()
