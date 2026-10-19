# Step 9 prompt algorithm — record decisions and verify the submission

Paste the prompt below into Codex or Claude Code from the repository root.

---

You are implementing **Step 9: record decisions, freeze the final candidate, reproduce it, and generate a verified Part 1 submission file** for the IAA AI-Assisted Actuarial Hackathon 2026 repository.

## Objective

Convert the accepted result from Steps 5–8 into one traceable, reproducible submission candidate. Step 9 is not another modelling or hyperparameter-search stage. Do not improve the model while packaging it. Freeze the selected design, refit it once on the approved full training period, predict the 2025 rows, and prove that the resulting CSV is structurally and financially coherent.

Creating and verifying a local submission file is authorised by this prompt. **Uploading to Kaggle, selecting a final Kaggle entry, committing, pushing, merging or publishing is not authorised.** Stop with an upload-ready file and explicit human decision points.

## 1. Read the evidence and establish the final-selection authority

Read, in this order:

1. `context.md`
2. `what-good-looks-like.md`
3. `AGENTS.md`
4. the current status, assumptions, decisions and unresolved-issues documents
5. the Step 1 prediction, scoring and submission contract
6. the Step 2–4 data, response and validation contracts
7. all Step 5–7 experiment manifests and model cards
8. `outputs/step8/decision.json`, the Step 8 acceptance report and candidate comparison
9. the current official Kaggle overview, data, evaluation and rules pages

Record the time and source of the rules check. Do not inherit stale statements about deadlines, daily submission limits or final-selection limits from old repository documents. If the live page cannot be accessed, state that the rule check is unresolved rather than guessing.

Inspect the working tree and preserve unrelated user changes. Update only the active-scope section of `AGENTS.md` to Step 9 while retaining all existing controls. Create `prompts/step9/00-finalise-and-verify.md` containing this execution contract.

## 2. Resolve the accepted model without reopening model selection

Use the following deterministic precedence:

1. If Step 8 says `promote_candidate` and every required promotion gate passed, select that candidate.
2. If Step 8 says `retain_benchmark`, select the frozen Step 8 benchmark.
3. If Step 8 says `inconclusive`, select the last simpler candidate that previously passed its acceptance gates; do not break the tie using 2024 results or expected leaderboard performance.
4. If Step 8 says `blocked`, or the selected model cannot be reproduced from its manifest, stop and report the blocker.

Create `configs/final_model.json` before refitting. Pin:

- model and code identifiers;
- repaired-data and claim-universe hashes;
- response version and maturity/recovery scenario;
- training years and financial valuation basis;
- feature allowlist and prohibited fields;
- preprocessing, exposure treatment and target units;
- model parameters and random seeds;
- prediction floor, if required solely for metric-domain safety;
- software/environment versions;
- the exact sample-submission source and expected row count.

Do not change the feature list, tune parameters, change the response scenario, optimise a blend, recalibrate to 2024, or use leaderboard results. Any required methodological change returns the workflow to the appropriate earlier step and makes Step 9 `blocked` until reapproved.

## 3. Complete the decision and AI-direction record

For every substantive decision from Steps 2–9, update a structured direction log with:

- issue or task;
- AI proposal;
- evidence checked;
- automated verification performed;
- actual human decision, if one exists;
- implementation and measured impact;
- unresolved uncertainty.

Do not describe an AI self-review as human approval. Do not invent review, sign-off, organiser confirmation or leaderboard evidence. Explicitly record important rejected proposals and corrections, including exposure repair, motor customer-ID repair, duplicate-claim treatment, sum-insured interpretation, claim maturity assumptions, leakage exclusions and any rejected model complexity.

Create `reports/step9/final-selection.md` explaining why the selected model follows from the frozen evidence. Distinguish measured facts, actuarial judgement and unresolved assumptions.

## 4. Perform one controlled full-training refit

Refit the frozen model using all approved 2021–2024 training rows and the exact response version selected above. This is a production refit, not a new experiment.

Requirements:

- rebuild from the repaired source layer rather than reusing an undocumented in-memory object;
- fit every imputer, encoder, scaler, feature transform and history calculation only from eligible training information;
- apply the validated exposure formulation exactly once;
- preserve line-specific models and any accepted decomposition or blend exactly as frozen;
- use no 2025 outcomes or submission feedback;
- use `row_id` only for alignment and reconciliation, never as a predictor;
- prohibit current claim amounts, final claim status, post-period contacts, `renewal_decision` and any other excluded or timing-unsafe feature;
- save the fitted model, preprocessing objects and feature schema;
- reload the saved artifacts and require predictions to match the pre-save predictions within a declared numerical tolerance.

If full-data refitting materially changes prediction distributions from the fold models, investigate it as a review alert. Do not silently recalibrate totals.

## 5. Generate the 2025 predictions

Score the three supplied 2025 test files. Build the submission by an explicit one-to-one join to the supplied sample `row_id`, then restore the exact sample row order.

The final file must have exactly:

```text
row_id,prediction
```

with no index or additional columns.

Write the primary candidate to a deterministic path such as:

`submissions/part1_<model_id>_<run_id>.csv`

Do not overwrite an existing file. Keep detailed diagnostics outside the submission CSV. Do not label the file as “ultimate” unless the recorded target construction genuinely supports that description; otherwise use the exact response/scenario identifier.

## 6. Enforce mechanical submission gates

After writing the CSV, reread it from disk and fail closed unless all checks pass:

- exactly 626,639 data rows;
- exactly two columns named `row_id` and `prediction`, in that order;
- no serialized index column;
- `row_id` is read and compared as a string;
- every `row_id` is non-null and unique;
- exact set equality with the sample-submission IDs;
- exact sample row order;
- line prefixes and row counts reconcile to the three test files;
- `prediction` parses as numeric for every row;
- no missing, infinite or non-finite predictions;
- no negative predictions;
- strictly positive predictions if required by the chosen Tweedie scorer, using only the predeclared numerical floor;
- predictions are policy-period costs, not annual rates;
- exposure has not been applied twice;
- predictions from the reloaded saved model reproduce the CSV within tolerance;
- a second deterministic run produces the same file hash, or any allowed nondeterminism is quantified and documented.

Add automated failure tests for duplicate IDs, missing IDs, extra IDs, reordered IDs, an index column, NaN/Inf values, negative values, zero-domain violations, accidental annual-rate output and incompatible input/model hashes.

## 7. Perform financial and actuarial review checks

Create `reports/step9/submission-diagnostics.md` containing at least:

- total predicted cost and predicted loss cost per exposure;
- totals by motor, buildings and contents;
- distribution statistics and selected quantiles by line;
- counts and totals for very small and very large predictions;
- comparisons with full-training observed/scenario totals and the corresponding validation-fold predictions;
- calibration evidence inherited from validation, clearly separated from test-set diagnostics;
- change in totals caused by the selected maturity, recovery or trend assumptions;
- new versus returning policy diagnostics where available;
- sensitivity of totals to any unresolved high-impact assumption;
- explanations for material discontinuities or implausible segments.

These checks are alerts, not targets. Do not force the submission total to equal premium, historical incurred cost or an uncertain prior forecast merely to make the report look reasonable.

## 8. Create immutable provenance

Create `outputs/step9/submission-manifest.json` containing:

- submission filename and SHA-256 hash;
- generation timestamp and run ID;
- Git commit SHA, plus dirty-worktree status and patch hash when applicable;
- all input, configuration, model and environment hashes;
- selected-model decision reference;
- response and feature versions;
- training and test row counts by line;
- prediction totals by line and overall;
- every mechanical gate and its result;
- every command needed to rebuild and recheck the file;
- upload status fixed to `not_uploaded`;
- human-review and final-selection status fixed to `pending` unless a real person has recorded otherwise.

Do not create a commit solely to populate the manifest. An honest dirty-state record is preferable to an invented clean provenance claim.

## 9. Execute a clean reproducibility run

Provide Make targets or equivalent commands for:

- `step9-check`
- `build-final-model`
- `build-submission`
- `verify-submission`
- `reproduce-step9`

Run the relevant unit tests, integration tests and a clean end-to-end rebuild from the repaired data layer. Ensure generated models, predictions and large outputs are ignored by Git unless the repository’s existing policy explicitly requires otherwise. Compare the reproduced SHA-256 hash with the manifest.

If exact byte-for-byte reproduction is impossible because of a documented library-level nondeterminism, require prediction equivalence within a strict predeclared tolerance and document why the file hash differs. Do not call the run exactly reproducible when only approximate equivalence was achieved.

## 10. Acceptance decision

Write `reports/step9/acceptance.md` and `outputs/step9/status.json` with one status:

- `ready_for_human_review`
- `blocked`
- `failed_verification`

`ready_for_human_review` requires:

1. a model selected strictly from prior frozen evidence;
2. a successful full-data refit and saved-model reload test;
3. all mechanical submission gates passed;
4. completed financial diagnostics with no unexplained critical alert;
5. successful clean reproduction;
6. complete provenance and decision records;
7. no false human-sign-off or Kaggle-upload claim.

Finish your response with:

1. selected model and governing decision;
2. exact response/scenario and training period;
3. commands and tests actually run;
4. submission path, row count, prediction total and SHA-256;
5. all failed or unresolved gates;
6. important actuarial limitations;
7. exact command for independent reproduction;
8. a clear statement: **“The file has not been uploaded to Kaggle.”**

## 11. Hard boundaries

- Stop after Step 9.
- Do not tune or add model complexity.
- Do not use leaderboard feedback to alter the candidate.
- Do not fabricate ultimate outcomes or historical financial snapshots.
- Do not contact the organisers.
- Do not upload to Kaggle or select a final Kaggle submission without separate explicit authorisation.
- Do not commit, push, merge, tag or publish unless explicitly requested.
- Do not claim actuarial validation, human approval, official metric equivalence or production readiness.
- Do not ask for routine permission between implementation substeps. Continue automatically unless a true blocker, missing authority or material inconsistency is encountered.

---

## Intended interpretation

Step 9 answers one question:

> Can the selected model be rebuilt from controlled inputs and turned into an exactly formatted, financially reviewed and fully traceable submission candidate without reopening model selection?

A verified local CSV is the deliverable. Kaggle upload and final-entry selection remain explicit human actions.
