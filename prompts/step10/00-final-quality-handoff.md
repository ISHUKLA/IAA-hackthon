# Step 10 prompt algorithm — final quality gate and Part 1 handoff

Paste the prompt below into Codex or Claude Code from the repository root.

---

You are implementing **Step 10: final quality review, controlled Part 1 packaging, and Part 2 handoff** for the IAA AI-Assisted Actuarial Hackathon 2026 repository.

## Objective

Determine whether the completed Part 1 work meets the user’s stated quality bar and is ready for human-authorised Kaggle upload. Consolidate the evidence into a concise, reproducible and honest package. Do not reopen model selection, tune parameters, alter predictions to improve presentation, or manufacture missing evidence.

Step 10 may repair documentation, paths, deterministic build scripts and non-substantive packaging defects. Any change to data treatment, response construction, feature eligibility, model parameters, calibration, prediction values or model selection is a methodological change and must be returned to the relevant earlier step.

This prompt authorises local quality checks and creation of a local Part 1 handoff package. It does **not** authorise Kaggle upload, final-entry selection, Git commit/push/merge/tag, publication, or contact with organisers.

## 1. Read the complete chain of evidence

Read, in this order:

1. `context.md`
2. `what-good-looks-like.md`
3. `AGENTS.md`
4. the current official competition overview, data, evaluation and rules pages
5. the current status, source register, assumptions, decisions and unresolved-issues documents
6. the Step 1 prediction, scoring and submission contract
7. the Step 2–4 data, response and validation acceptance evidence
8. the Step 5–8 model experiments, manifests, decisions and model cards
9. the Step 9 final-model configuration, selection report, submission diagnostics, acceptance report and submission manifest
10. the actual final candidate CSV and all scripts required to reproduce it

Record the access date and URLs for the official rules. Extract the current deadline, required deliverables, judging criteria and weights, submission limits, final-selection rules and any Part 1-specific instructions. Quote exact official wording only where useful and preserve source links. If a page cannot be accessed or conflicts with repository notes, mark the issue unresolved and do not guess. Current official instructions take precedence over stale planning notes, but never silently rewrite the historical record.

Inspect the working tree and preserve unrelated changes. Update only the active-scope section of `AGENTS.md` to Step 10 while retaining all existing controls. Create `prompts/step10/00-final-quality-handoff.md` containing this execution contract.

## 2. Freeze the Step 9 candidate

Treat the Step 9 submission candidate and its SHA-256 hash as immutable during this review. Verify that:

- Step 9 status is `ready_for_human_review`;
- the selected model follows the documented Step 8 decision;
- the submission file exists at the manifest path;
- the file hash, row count, prediction total and model/configuration hashes match the manifest;
- the recorded code state and environment are available;
- upload status remains `not_uploaded` unless there is verifiable evidence otherwise.

If any check fails, mark Step 10 `blocked` or `failed_verification`. Do not regenerate a different file and call it the same candidate. A byte-identical rebuild using the frozen configuration is permitted; a changed prediction file requires a new Step 9 run and new manifest.

## 3. Build a traceable quality-bar matrix

Create `reports/step10/quality-bar-matrix.md`. Translate every material requirement from `what-good-looks-like.md`, `context.md` and the current official judging criteria into a row with:

- requirement;
- source;
- status: `pass`, `partial`, `fail`, `not_applicable`, or `not_testable`;
- exact evidence path and section;
- verification performed;
- limitation or missing evidence;
- required action and owner.

At minimum, evaluate the following domains.

### Actuarial judgement

- correct distinction between expected ultimate policy-period cost and observed incurred proxy;
- treatment and disclosure of exposure, claim matching, duplicates and recoveries;
- reporting delay, open-claim maturity, large-loss and future-recovery uncertainty;
- sensitivity to the largest bodily-injury claim and material immature perils;
- clear separation of measured facts, assumptions and judgement;
- no claim of identified ultimate truth from a single financial snapshot.

### Pricing and modelling competence

- chronological validation matching the likely 2025 forecasting task;
- leakage-safe features and train-only preprocessing;
- transparent baselines and same-row paired comparisons;
- correct Tweedie power, target units and exposure treatment;
- calibration, segment, new/returning and tail diagnostics;
- complexity promoted only when supported by out-of-sample evidence;
- honest handling of reused challenge data and target uncertainty.

### Effective AI use

- actual prompts, proposals, corrections and decisions are recorded;
- AI-generated claims were verified against code, data or primary sources;
- concrete examples show where human judgement accepted, rejected or modified an AI proposal;
- no fabricated human review, time savings, sign-off or AI contribution;
- the workflow is usable and auditable rather than merely a narrative about AI.

### Trust, reproducibility and governance

- raw data unchanged and repaired layers traceable;
- data, configuration, code, model and prediction hashes retained;
- environment and commands pinned sufficiently for reproduction;
- tests cover invariants, leakage, alignment and model reload;
- limitations, unresolved decisions and failure states remain visible;
- no secrets, credentials, personal information or large raw data are included in the package;
- no unlicensed or prohibited external data/code is used.

### Communication and professional usefulness

- the first page states the problem, selected approach, main evidence and limitations;
- terminology and units remain consistent;
- tables show decisions and measured results rather than process theatre;
- the submission can be explained to both an actuarial reviewer and a technical reviewer;
- the Part 2 handoff is concrete and does not presume the new data will behave like Part 1.

Do not award a pass because a document exists. Inspect whether it contains the required evidence. AI self-assessment is not independent human approval.

## 4. Recheck reproducibility and submission invariants

Run the Step 9 verification command against the frozen file. Re-run only the bounded tests needed to confirm that the current repository state still reproduces the recorded candidate. Use an isolated temporary workspace or other safe clean-run mechanism where practical; do not destroy the user’s working tree and do not commit merely to obtain a clean status.

Confirm again:

- 626,639 data rows;
- exactly `row_id,prediction` in that order and no index;
- unique, non-null IDs in exact sample order and exact test-ID coverage;
- finite numeric predictions in the permitted domain;
- one-to-one reconciliation to motor, buildings and contents test rows;
- policy-period cost units and exposure applied exactly once;
- saved-model reload equivalence;
- submission SHA-256 and financial totals match the Step 9 manifest;
- no target, outcome or future-information feature entered the final model;
- a clean or faithfully snapshotted rebuild gives the documented result.

If exact byte reproduction is not achieved, distinguish harmless serialization/formatting variation from changed numeric predictions. Do not call approximate numerical agreement byte-for-byte reproducibility.

## 5. Triage gaps without contaminating the model

Classify every discovered issue as:

1. **Documentation gap** — may be corrected in Step 10 without changing analytic outputs.
2. **Mechanical packaging defect** — may be fixed only if predictions and their meaning remain unchanged; rerun all file gates and issue a new package hash.
3. **Methodological defect** — return to the responsible earlier step; Step 10 becomes blocked.
4. **Unresolved assumption** — disclose it and assess whether it is tolerable for submission or blocks readiness.
5. **Human decision pending** — create a concise decision request; do not answer it on the user’s behalf.

Do not hide a failed quality criterion by weakening its wording. Do not make post-hoc model changes based on how a judge might react.

## 6. Produce the concise Part 1 narrative

Create or update a compact, evidence-linked documentation set:

- `docs/part1/executive-summary.md`
- `docs/part1/methodology.md`
- `docs/part1/results-and-diagnostics.md`
- `docs/part1/limitations-and-assumptions.md`
- `docs/part1/ai-use-and-human-oversight.md`
- `docs/part1/reproducibility.md`

The executive summary must lead with:

1. what is predicted and in what units;
2. the selected model and why it was selected;
3. the strongest validation evidence;
4. the most important data corrections;
5. the central limitation: the supplied claims are a December 2024 snapshot rather than observed ultimate outcomes;
6. what the final file contains and what has not yet been authorised.

Keep the narrative proportionate. Prefer compact result tables with exact fold, response and model IDs. Do not describe cards, SHAP plots or model complexity as proof of quality by themselves. Do not claim professional-standard compliance unless the exact standard was checked and the evidence meets it.

## 7. Consolidate the real AI audit trail

Create `docs/part1/ai-direction-log.md` or update the established equivalent. Summarise only real, evidenced episodes using:

```text
task → AI proposal → check performed → human decision/status → implementation → measured consequence
```

Include the most material examples, such as:

- discovery and correction of exposure corruption;
- repair of lost leading zeros in motor customer IDs;
- identification and treatment of duplicate claim candidates;
- challenge to unsupported ultimate/development assumptions;
- leakage quarantine decisions;
- the GLM-versus-LightGBM comparison;
- any complexity rejected because it failed the evidence gate.

Where no human decision has yet been recorded, state `human review pending`. Do not retroactively portray automated execution as human oversight.

## 8. Prepare the Part 2 adaptation handoff

Create `docs/part2/handoff-from-part1.md` without running Part 2. Include:

- frozen Part 1 input, schema, feature, response, fold, model and submission identifiers;
- components designed for reuse and components tied specifically to Part 1;
- a schema-and-distribution comparison checklist for new Part 2 data;
- assumptions that must be retested rather than carried forward;
- tests for changed columns, categories, missingness, units, exposure, date ranges, claim status, reporting lags and target definition;
- a prioritized adaptation order: data contract, response contract, validation, baselines, features, model challenger, submission;
- explicit prohibition on blindly applying Part 1 corrections or fitted models to Part 2;
- the minimum evidence needed before claiming adaptation success.

This handoff demonstrates adaptability through reusable controls, not by predicting what the unseen Part 2 dataset will contain.

## 9. Build a controlled handoff manifest

Create `outputs/step10/part1-handoff-manifest.json` listing:

- frozen submission filename and SHA-256;
- final model and configuration IDs;
- code/Git state and environment identity;
- required reproducibility commands;
- included reports, model cards, logs and their hashes;
- official-rule check timestamp and unresolved rule questions;
- all quality-bar statuses;
- all outstanding assumptions and human decisions;
- upload status `not_uploaded`;
- final Kaggle-entry selection status `pending`;
- Part 2 execution status `not_started`.

Generate a package inventory or local archive only if required by the official instructions or existing project workflow. Exclude raw data, secrets, caches, virtual environments, unnecessary model-search artifacts and absolute machine-specific paths. Verify any archive by listing and hashing its contents. Do not publish it.

## 10. Make the readiness decision

Create `reports/step10/final-readiness.md` and `outputs/step10/status.json` with exactly one status:

- `ready_for_part1_upload`
- `ready_with_disclosures`
- `blocked`
- `failed_verification`

Use these meanings:

- `ready_for_part1_upload`: all critical analytic, mechanical and reproducibility gates pass; only explicit human upload/final-selection actions remain.
- `ready_with_disclosures`: the package is mechanically valid and reproducible, but non-critical unresolved assumptions must be acknowledged before upload.
- `blocked`: a methodological, rules, authority or missing-evidence issue prevents a defensible submission.
- `failed_verification`: the frozen candidate or package does not reproduce or fails an invariant.

Do not average quality scores to conceal a critical failure. Treat target leakage, incorrect exposure use, incompatible response versions, broken ID coverage, non-reproducible predictions, unknown official deliverables or false provenance as blockers.

Create a short human checklist covering only genuine remaining decisions:

- accept the documented response/ultimate limitations;
- accept the selected model and prediction total;
- verify the displayed submission filename and SHA-256;
- review unresolved assumptions and rule questions;
- authorise Kaggle upload separately;
- select the final Kaggle entry separately, in accordance with the current rules.

Leave every item unchecked unless a real human has explicitly completed it.

## 11. Commands and acceptance tests

Provide repository-consistent commands such as:

- `make step10-check`
- `make verify-part1-package`
- `make reproduce-part1`
- `make step10-acceptance`

Run the relevant commands and record their actual results, runtime and environment. Do not claim that a command exists or passed unless it was executed successfully. If the repository uses another task runner, use its established convention rather than adding decorative Make targets.

Step 10 acceptance requires:

1. the Step 9 file remains frozen and verified;
2. the full quality matrix is evidence-linked;
3. critical gaps are resolved or explicitly block readiness;
4. the concise Part 1 narrative is internally consistent;
5. the AI audit trail contains only real events;
6. the Part 2 handoff is complete but Part 2 has not been run;
7. the handoff manifest is complete and reproducible;
8. no external upload, publication or invented human approval occurred.

## 12. Final response

Finish with:

1. the Step 10 readiness status;
2. selected model, response version and submission SHA-256;
3. quality-bar results by domain;
4. tests and reproduction commands actually run;
5. unresolved assumptions and blockers;
6. documentation and Part 2 handoff created;
7. the exact next human decisions;
8. these explicit statements:

```text
The submission file has not been uploaded to Kaggle.
No final Kaggle entry has been selected.
Part 2 has not been executed.
```

## 13. Hard boundaries

- Stop after Step 10.
- Do not change the frozen model or predictions.
- Do not tune against validation, test predictions or leaderboard feedback.
- Do not fabricate ultimate outcomes, sign-off, professional compliance, AI impact or reproducibility.
- Do not upload to Kaggle, select a final entry, contact organisers, commit, push, merge, tag or publish without separate explicit authorisation.
- Do not run Part 2.
- Do not ask for routine approval while performing authorised local checks and documentation. Stop only for a real authority boundary, missing evidence, irreproducible candidate, unresolved official requirement or methodological defect.

---

## Intended interpretation

Step 10 answers:

> Is the complete Part 1 result analytically defensible, reproducible, clearly communicated and ready for an informed human upload decision?

The correct result may be `blocked`. A polished package must never conceal an unsupported target, leakage, non-reproducibility or missing human judgement.
