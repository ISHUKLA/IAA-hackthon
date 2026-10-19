# Address-feature GLM challenger — 19 October 2026

## Scope and source

This is a separate experiment, not a revision of the frozen S6/S9 models or an automatic final-entry selection. The direct user request was to add `flood_zone`, `elevation_m` and `distance_to_river_km` to buildings and contents GLMs and also try `bedrooms`, `property_type` and `year_built`. All six are from the supplied `addresses.parquet`, joined to repaired policy rows on `address_id`. Its SHA-256 is `2f1a9a157649a73ed1b0ee9b2caa3660b4c2a11766af3c64ab5131389079c0b1`, matching the frozen raw-input identity. The dimension has 575,983 unique non-null address keys. The guarded many-to-one join covered all 1,429,343 home training rows without row multiplication or reordering; no `year_built` exceeded its policy inception year. The sole available address snapshot has no historical version timestamps, so literal as-of availability in 2021–2024 cannot be proven. The current fields are plausibly quote-time, not independently time-stamped.

`flood_zone` is an explicit categorical zone 1–5 plus `missing` (16,823 dimension rows missing). Elevation, river distance, bedrooms and year built are numeric; numeric imputation, scaling, one-hot vocabularies and missing indicators are fitted on each fold's training rows only. The power-1.5 log-link Tweedie GLM, alpha 1, exposure rate weighting and one final exposure multiplication are otherwise unchanged. Neither raw data nor the old fitted models/CSVs were overwritten.

## Registered comparisons and decision

The 2023 primary fold tested each of the three geography fields separately, the three together, the three property-characteristic fields together and all six on the repaired observed-snapshot response. The grouped candidates were repeated on the 2024 challenge. The same grouped candidates were independently fitted/scored on the previously constructed, assumption-dependent conditional-ultimate response. Every reported D² is **local unweighted policy-period Tweedie D² at power 1.5 on an end-2024-valued retrospective target**, not an official leaderboard score or observed ultimate accuracy.

The individual F2023 observed-snapshot probes show overlap: buildings D² was 0.061250 baseline, 0.093656 with flood zone, 0.069167 with elevation, 0.066304 with distance and 0.093828 with all three geography fields. Contents was 0.045682 baseline, 0.072019 flood, 0.050371 elevation, 0.052989 distance and 0.072571 with the three together. The three property-characteristic fields alone reached 0.063192 buildings and 0.045742 contents. These are measured changes, not a sum-of-gains estimate.

The primary F2023 conditional-target comparison selected **all six** for buildings and **only the three geography fields** for contents: all six improved buildings beyond geography alone, while contents all-six D² (0.072560) was marginally below geography alone (0.072571). F2024 was inspected as a challenge, not used to choose the fields. Motor predictions stay unchanged. The earlier Step 6 and conditional-ultimate candidates remain intact; this selection is an experimental candidate, not actuarial approval.

| Conditional target | F2023 baseline → selected D² | F2024 baseline → selected D² |
| --- | ---: | ---: |
| Buildings | 0.064165 → 0.100366 | 0.069166 → 0.116910 |
| Contents | 0.045682 → 0.072571 | 0.059185 → 0.084500 |
| All lines pooled, motor unchanged | 0.126534 → 0.143875 | 0.139547 → 0.163098 |

On the repaired observed-snapshot sensitivity, the same selected combination improved pooled F2023 D² from 0.113452 to 0.129229 and pooled F2024 from 0.089801 to 0.107858. Different target versions have different null deviances: compare candidates **within** a target/fold, not across those rows.

## Conditional-target actual/expected by flood zone

Each cell is baseline A/E → selected A/E; `n` is the number of held-out policy-period rows. These ratios use the constructed conditional response. Flood-zone 5 remains materially underpredicted even after the improvement.

| Line | Zone | F2023 n | F2023 A/E | F2024 n | F2024 A/E |
| --- | --- | ---: | ---: | ---: | ---: |
| Buildings | missing | 5,350 | 1.721 → 1.028 | 5,418 | 2.772 → 1.741 |
| Buildings | 1 | 126,310 | 0.814 → 1.032 | 125,875 | 0.850 → 1.074 |
| Buildings | 2 | 27,141 | 0.905 → 0.943 | 27,255 | 0.944 → 0.985 |
| Buildings | 3 | 14,576 | 1.090 → 0.864 | 14,626 | 1.328 → 1.086 |
| Buildings | 4 | 8,133 | 3.114 → 1.504 | 8,612 | 2.900 → 1.364 |
| Buildings | 5 | 2,622 | 6.901 → 2.390 | 2,215 | 6.468 → 2.250 |
| Contents | missing | 5,461 | 2.027 → 1.510 | 5,484 | 1.890 → 1.344 |
| Contents | 1 | 128,742 | 0.818 → 0.979 | 128,357 | 0.831 → 1.005 |
| Contents | 2 | 27,535 | 0.947 → 0.913 | 27,644 | 0.954 → 0.915 |
| Contents | 3 | 14,783 | 1.312 → 1.010 | 14,846 | 1.537 → 1.185 |
| Contents | 4 | 8,408 | 2.724 → 1.657 | 8,877 | 2.452 → 1.444 |
| Contents | 5 | 2,717 | 7.025 → 3.085 | 2,283 | 4.701 → 2.063 |

Pooled D² improved despite some total A/E ratios moving further above one; no post-hoc flood-zone calibration was fitted. High-zone severity, missingness and conditional target adequacy need independent actuarial review. The 2024 fold remains an immature, previously reused challenge rather than an independent prospective ultimate backtest.

## Local 2025 file and the unmeasurable 2025 D²

The new separate CSV is `submissions/part1_conditional_property_b4cd47c40def328f.csv`, SHA-256 `4fdc84b4edba95453b2e3453246640377d70bd3a36ec92f7a15c2dfe1dd81991`. It has all 626,639 exact sample-order IDs and strictly positive finite policy-period predictions. Total is 195,647,622.24 CU (motor 113,990,416.73 unchanged; buildings 64,589,364.79; contents 17,067,840.72), 2,718,099.36 CU below the prior conditional candidate. Buildings/contents full fits converged in four/three iterations, and saved-model reload predictions were exactly equal. An independent second full fit and CSV serialization reproduced the same CSV SHA-256. The separate CSV checker passed. No Kaggle upload or final-entry selection occurred.

**There is no measured 2025 D².** Direct schema checks found no claim/incurred/ultimate/recovery outcome field in any of the three 2025 test Parquets or the 626,639-row sample. D² requires both outcomes and predictions. A validation-fold D² must not be renamed a 2025 score. Exact scorer pooling and any private leaderboard score also remain unverified.

## Reproduce and limitations

With the prior ignored repaired/fold/S6/conditional-ultimate artifacts available and `IAA_DATA_DIR` set to the original public-data directory, run from the repository root using fresh output paths:

```sh
PYTHONPATH=src .venv/bin/python scripts/run_property_features.py --data-dir "$IAA_DATA_DIR" --output-dir outputs/property-recheck-observed --target observed
PYTHONPATH=src .venv/bin/python scripts/run_property_features.py --data-dir "$IAA_DATA_DIR" --output-dir outputs/property-recheck-conditional --target conditional
PYTHONPATH=src .venv/bin/python scripts/summarize_property_features.py --output-dir outputs/property-recheck-observed --selected
PYTHONPATH=src .venv/bin/python scripts/summarize_property_features.py --output-dir outputs/property-recheck-conditional --selected
PYTHONPATH=src .venv/bin/python scripts/build_property_candidate.py --data-dir "$IAA_DATA_DIR" --challenge-dir outputs/property-recheck-conditional --output-dir outputs/property-recheck-full --csv-dir outputs/property-recheck-full/submissions
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Runtimes and serialized model hashes can vary across environments; the selection config records the original result-file hashes but fresh runs are checked by upstream/config identities and primary/challenge outcomes rather than requiring runtime-bearing JSON bytes to match. The frozen S9 configuration/code and both older CSVs were not modified. This candidate still inherits the unverified recovery-netting basis, case adequacy, stable mature-rate/IBNR assumptions, sum-insured repairs and single address snapshot. Human target, calibration and deployment decisions remain pending.

Verification after the source changes: `PYTHONPATH=src .venv/bin/python -m pytest -q` passed 195 tests (one environment-only physical-core warning); Python compilation and `git diff --check` passed; the independent CSV validator confirmed exact columns, 626,639 IDs/order and strictly positive finite values; two full builds produced the same CSV SHA-256. Git exclusions ignore the candidate CSV, models and row-level outputs. The broad `make check PYTHON=.venv/bin/python` still fails on the already tracked, unchanged `reports/d2_summary.csv`, which its no-tracked-CSV policy rejects. That unrelated pre-existing file was preserved.
