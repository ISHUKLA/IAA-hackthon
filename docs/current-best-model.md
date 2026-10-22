# Current best Part 1 model

Status recorded 22 October 2026.

## Champion identity

| Item | Value |
|---|---|
| Model/candidate | `buildings-level-v1` |
| Parent | `home-catboost-retune-v1` |
| Submitted filename reported by the user | `IAA_2025_buildings_level_uplift_v1.csv` |
| Public leaderboard D² reported by the user | **0.12483** |
| Parent public D² reported by the user | 0.12477 |
| Reported public change | **+0.00006** |
| Submission CSV SHA-256 | `d0476e68259365d7876c864474d8870f5ff8173b2e01ea927c18b09e53604fb1` |
| Local artifact | `outputs/buildings-level-v1/submission.csv` (Git ignored) |
| Row contract | 626,639 rows; columns `row_id,prediction`; sample order |

The user explicitly instructed that this model be kept. It is the current best Part 1 submission until a later, explicitly identified file receives a higher verified score and is adopted.

## Exact change from the parent

The candidate starts from the final predictions of `home-catboost-retune-v1` and applies one post-model calibration factor:

```text
motor:      parent prediction × 1
buildings:  parent prediction × 1.0421200248616982
contents:   parent prediction × 1
```

The buildings factor is the 50% credibility shrinkage of the exposure-weighted buildings A/E gap from the saved F2023 and F2024 predictions. The predeclared 1.05 cap did not bind. The existing parent trend is already present in the predictions and is not applied again. No model was refitted, and no feature, target, blend weight, row ID, ordering, or CSV schema changed.

The generated file was checked against the sample submission and all three raw test ID sets. Motor and contents predictions are identical to the parent. The buildings mean increased from 412.804316 to 430.191644, or 4.2120%.

## Reproducibility record

- Configuration: `configs/buildings_level_v1.json`
- Implementation: `src/iaa_hackathon/buildings_level.py`
- Runner: `scripts/run_buildings_level.py`
- Tests: `tests/test_buildings_level.py`
- Full experiment report: `reports/buildings-level-v1.md`
- Generated manifest: `outputs/buildings-level-v1/manifest.json` (Git ignored), SHA-256 `94c873bb950edf676aaf0466cba78c0e54bb8686d69b4bf8d42599a9c6e0feff`

The CSV and manifest stay outside Git because repository policy ignores generated outputs. Their hashes pin the retained local artifacts. Rebuilding requires the hash-pinned parent submission, parent fold predictions, repaired model tables, sample submission, and raw test files described in the report and manifest.

## Evidence boundary

The score and mapping from the submitted filename to the hashed CSV are user-reported; this repository update did not retrieve them independently from Kaggle. The +0.00006 public movement is small and applies to the public leaderboard subset. The local fold improvements are circular because the same F2023/F2024 A/E values determined the factor. The constructed conditional-ultimate target, recovery treatment, case adequacy, and validation reuse remain documented limitations.

The separate factor-1.05 candidate is not the champion: it has no public score because submission access was blocked. Segment and predicted-risk-shape calibration follow-ups were rejected by their declared local gates. They do not replace this file.
