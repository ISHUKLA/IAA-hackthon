# Buildings-only level uplift — 22 October 2026

## Result

Generated a separate buildings-level exploratory candidate from the hash-pinned `home-catboost-retune-v1` submission. No model was fitted and no feature, target, blend weight or trend was changed. Only 2025 buildings period-cost predictions were multiplied by the derived factor; motor and contents remain byte-for-byte equal at the prediction-value level to the parent.

The user subsequently identified this exact CSV as the submitted file and reported a public leaderboard D² of **0.12483**, compared with **0.12477** for its `home-catboost-retune-v1` parent: a public improvement of **+0.00006**. The file is therefore retained as the current best Part 1 submission. The score and file-to-submission mapping are user-reported and were not independently retrieved from Kaggle. The result is public-subset evidence only; it does not remove the validation and target limitations below.

## Calibration and factor

A/E is defined here as aggregate actual divided by aggregate predicted. The outcome used is the saved `conditional-ultimate-v1` row target, not observed 2025 ultimate claims. Fold rows, target fingerprints and prediction Parquet hashes were checked against the parent manifest. Fold exposures came from `exposure_clean`, the cleaned exposure convention used in the pricing pipeline.

| Fold | Buildings rows | Actual total | Parent predicted total | A/E | Total `exposure_clean` |
|---|---:|---:|---:|---:|---:|
| F2023 | 184,132 | 64,957,957.04 | 58,919,239.96 | 1.102491429 | 149,987.3017 |
| F2024 | 184,001 | 71,254,921.44 | 66,844,508.99 | 1.065980176 | 149,917.5224 |

Exposure-weighted fold A/E:

```text
(1.102491429 × 149,987.3017 + 1.065980176 × 149,917.5224)
/ (149,987.3017 + 149,917.5224) = 1.084240050
```

The requested half-gap factor is `1 + 0.5 × (1.084240050 - 1) = 1.042120025`. The 1.05 upper cap does not bind. It is applied after the parent trend by multiplying the already-produced 2025 buildings predictions; there is no second trend or exposure application.

## Local score transparency (circular; not a gate)

The same two folds determine the uplift and are then used to score it. These values are therefore circular diagnostics, not independent validation or a reason to adopt the adjustment.

| Fold / scope | Parent D² | Uplift D² | Change | Parent A/E | Uplift A/E |
|---|---:|---:|---:|---:|---:|
| F2023 buildings | 0.112964797 | 0.113399864 | +0.000435067 | 1.102491 | 1.057931 |
| F2023 pooled | 0.157235053 | 0.157382993 | +0.000147940 | 1.106172 | 1.091423 |
| F2024 buildings | 0.135323835 | 0.135547403 | +0.000223569 | 1.065980 | 1.022896 |
| F2024 pooled | 0.183671384 | 0.183756253 | +0.000084869 | 1.099739 | 1.083240 |

The F2023 table includes `M01176324`; the uplift itself affects buildings only. No gate was applied, consistent with the request.

## 2025 output and checks

| Line | Parent mean | Candidate mean | Change |
|---|---:|---:|---:|
| Motor | 411.953388 | 411.953388 | 0% (identical) |
| Buildings | 412.804316 | 430.191644 | +4.2120% |
| Contents | 101.738887 | 101.738887 | 0% (identical) |

`outputs/buildings-level-v1/submission.csv` has 626,639 rows and exactly the `row_id,prediction` header; IDs and order match `sample_submission.parquet`. All three raw test files were hash-verified and their IDs exactly reconcile to the CSV by line (254,986 motor; 184,155 buildings; 187,498 contents). There are no duplicate IDs; predictions are finite and nonnegative; motor and contents equal the parent; every building prediction equals its parent value multiplied by the factor.

CSV SHA-256: `d0476e68259365d7876c864474d8870f5ff8173b2e01ea927c18b09e53604fb1`.

Current-best registry: `docs/current-best-model.md`.

The implementation and tests are `src/iaa_hackathon/buildings_level.py`, `scripts/run_buildings_level.py`, `configs/buildings_level_v1.json` and `tests/test_buildings_level.py`. Reproduce with:

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_buildings_level.py
PYTHONPATH=src .venv/bin/python -u scripts/run_buildings_level.py --data-dir '/Users/coralieroland/Desktop/IAA Hackathon/public'
```

The builder refuses to overwrite an existing output directory. Focused tests: 8 passed. Full suite: 362 passed, one environment physical-core warning. Compilation and `git diff --check` passed. The first full-suite invocation omitted `scripts` from `PYTHONPATH` and failed test collection; rerunning with the repository convention `PYTHONPATH=src:scripts` passed. Run time: 17.79 seconds. At generation time, no upload, commit or push was made and the human decision field was blank. The later user instruction retained this exact file as the current best based on the user-reported public result above. Do not interpret the circular fold score changes as 2025 D²; actual 2025 outcomes are unavailable.

## Limitations

The factor was selected directly from the same F2023/F2024 A/E values on which its local scores are shown. F2024 has also been reused in earlier experiments. `conditional-ultimate-v1` is a constructed proxy target, not claim-level observed ultimate; the financial basis, valuation and development assumptions remain unresolved. A/E calibration toward one does not by itself establish better predictive accuracy or actuarial approval.
