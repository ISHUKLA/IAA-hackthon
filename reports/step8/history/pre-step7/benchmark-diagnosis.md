# Step 8 benchmark preflight — blocked

Date: 19 October 2026. The supplied execution contract requires an explicit stop when Steps 5–7 evidence is missing or irreproducible. Two independent blockers were measured locally:

1. No Step 7 experiment manifest, fitted model, held-out prediction, comparison or acceptance report exists under the local Step 7 output/document/prompt directories. Current status and the Model Card also record that Step 7 was not executed. A proposed nonlinear model in the plan is not completed evidence.
2. `outputs/step4/folds/fold-membership.parquet` cannot be decoded. A full pandas read failed with `OSError: Corrupt snappy compressed data.` An independent streaming PyArrow read failed while deserializing a Parquet page header. The file has SHA-256 `d86ba94648e7a6f3368b5a5580bb1aee93f04d5d307af89eadbb8f30290a0710`. Its contents have not been replaced. Exact agreement with the saved fold membership and its logical digest cannot currently be verified.

The repaired training table and four saved S5/S6 GLM prediction files passed independent streaming reads. All 16 repair-audit output hashes matched, as did the S5/S6 config and implementation hashes and the repaired response/reporting artifact hashes. Rescoring saved predictions against calendar-year rows in the current repaired table reproduced their pooled metrics to tolerance `rtol=atol=1e-12`. This independently preserves useful evidence, but does not bypass the unreadable frozen membership.

The best available S5/S6 model is the S6 selected compact Tweedie GLM: primary F2023 mean deviance/D² `103.49608782239278 / 0.11345157013436835`; prior challenge F2024 `99.43930802654187 / 0.08980138282838457`. The exact features, fitted-artifact hashes, settings, input hashes, response version and current scorer hashes are captured in ignored `outputs/step8/decision.json`. Its status is an available-model snapshot, not a qualified Step 8 benchmark across Steps 5–7.

Prior S6 diagnostics report an overall F2024 A/E of `0.9088900586803975`, including `0.8034309705954918` for motor, and concentration from the 11.89m CU F2023 bodily-injury claim. These are facts about a 31 December 2024 snapshot proxy. Response maturity, financial basis, timing and repair adoption remain unresolved; those observations alone do not establish that additional model complexity is the remedy. F2024 has already been inspected during S5/S6 and must be described as a reused development challenge.

Primary modelling weakness: **not selected** while preflight is blocked. Prediction-decile/exposure-band residual analysis, bootstrap uncertainty, new tail tests and candidate fitting were not run. Saved-model reload equivalence and peak memory were not measured by this preflight. No candidate family or numerical promotion threshold was invented.

Next prerequisite: supply or complete Step 7 on the same repaired inputs, response and frozen protocol, and explicitly resolve the unreadable Step 4 membership with provenance verification. Then rerun the Step 8 execution contract. Restoring this prerequisite is separate from silently refitting or rewriting prior model results.
