# Step-by-step prompt algorithm — Step 0 and Step 1
Use one prompt per turn in your coding harness. The starter already contains Step 0 files; Prompt 00 verifies and adapts them to your machine. Prompts 01–07 have not been executed.
## Execution loop

1. Run the harness from the repository root.
2. Ask it to read AGENTS.md and execute only the next prompt.
3. Review the changed files and actual command results.
4. Resolve a genuine actuarial choice or record a permitted provisional assumption; do not manufacture approval.
5. Continue to the next prompt only when its predecessor has met the stated acceptance criteria.
6. If a check fails, fix the current stage and rerun the relevant check before continuing.
7. After a reset/compaction, read AGENTS.md, docs/status.md, docs/assumptions.md and the current prompt again.
## Launch commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
export IAA_DATA_DIR="$HOME/Desktop/IAA Hackathon/public"
make check
make doctor
claude
```

IAA_DATA_DIR points to the files already on your computer. If the folder differs, change that single path. A cloud harness needs its own authorised data access; GitHub does not provide the local Desktop files.
## Prompt sequence

| Order | Ask the harness | Expected result |
| --- | --- | --- |
| 00 | `Read AGENTS.md. Execute only prompts/00-scaffold.md.` | Establish the repository |
| 01 | `Read AGENTS.md. Execute only prompts/01-sources.md.` | Ground the task and source register |
| 02 | `Read AGENTS.md. Execute only prompts/02-data-inventory.md.` | Verify input readiness without changing data |
| 03 | `Read AGENTS.md. Execute only prompts/03-prediction-contract.md.` | Specify target, exposure and assumptions |
| 04 | `Read AGENTS.md. Execute only prompts/04-metric.md.` | Implement and verify the metric contract |
| 05 | `Read AGENTS.md. Execute only prompts/05-submission-contract.md.` | Verify submission structure without generating predictions |
| 06 | `Read AGENTS.md. Execute only prompts/06-challenge.md.` | Challenge the Step 1 contract |
| 07 | `Read AGENTS.md. Execute only prompts/07-handoff.md.` | Verify and hand over Step 1 |

The following sections contain the complete prompt text, so this file can be used independently after the repository is present.

## Prompt 00 — Establish the repository

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Create or verify Step 0. This is infrastructure, not Step 1 actuarial implementation.

## Procedure
1. Inspect the working directory and git status. If the starter exists, preserve it. If creating from scratch, use the layout described in README.md: root briefs/instructions, prompts/, configs/, docs/evidence/, src/iaa_hackathon/, tests/fixtures/synthetic/, schemas/, scripts/, data/ and outputs/.
2. Read context.md then what-good-looks-like.md. Keep originals unchanged. If absent, report them as missing; do not manufacture replacements from memory.
3. Verify CLAUDE.md points to AGENTS.md and the latter defines the current scope and source precedence.
4. Create/verify pyproject.toml, a standard-library read-only doctor command, .gitignore, scaffold checks and read-only CI. Do not create dummy target, model or scorer functions. Do not add numerical dependencies just to check the scaffold.
5. Use a local virtual environment with Python 3.12. Install the local package. Run make check and the CLI help. Verify IAA_DATA_DIR if it is set. A missing local path is configuration to report, not justification for searching the entire computer.
6. Inspect Git exclusions for a raw Parquet, archive and prediction CSV. Do not add real records as test fixtures. Do not push or choose a licence.
7. Update docs/status.md and PROMPT_LOGS.md with actual results. Leave Step 1 and human review pending.

## Acceptance
The local package installs, help runs, scaffold checks pass, raw inputs/outputs are excluded, and no model/metric implementation is falsely claimed. Scope: Step 0 only. Next: Prompt 01.

---

## Prompt 01 — Ground the task and source register

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Establish the authoritative task and conflicts before writing contract code.

## Procedure
1. Read context.md, then what-good-looks-like.md, then official Kaggle overview/data/evaluation/rules. Reuse dated extracts in docs/evidence/competition-sources.md when live access is blocked; distinguish prior verification from a new retrieval.
2. Read docs/evidence/known-findings.md and docs/plan.md. Separate official requirements, measured data findings, interpretations, user choices and unresolved assumptions.
3. Write docs/step1/source-register.md with source URL/path, section, date/status, supported claim and limitation. Quote the metric name and CSV illustration exactly; do not fabricate unavailable text or reproduce entire pages.
4. Explain the task in five plain sentences: one row's unit, loss-date inclusion, ultimate meaning, expectation rather than guaranteed outcome, and net financial basis.
5. Record conflicts: predetermined ensemble versus conditional comparison; page-one layout; immature 2024 holdout; unverified mandatory-governance claims; scoring semantics; rules/overview discrepancy. Preserve existing explicit user choices unless recording a proposed change.
6. Update the assumption register and logs. Do not contact organisers or accept terms.

## Acceptance
Every material fact has a source/status. Exact scoring weights/pooling remain unresolved unless a primary source actually establishes them. Missing access is recorded without blocking definitions that are already supported. Next: Prompt 02.

---

## Prompt 02 — Verify input readiness without changing data

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Confirm that the local files support the proposed contract. Do not perform full cleaning, target construction or reserving.

## Procedure
1. Resolve IAA_DATA_DIR or the explicitly supplied directory. Run the doctor. Install only the dependencies needed for Parquet metadata/key inspection, recording changes.
2. Add a read-only inventory command. Read the eleven Parquet schemas, row counts and SHA256 hashes; compare with docs/evidence/expected-manifest.json. Reuse hashes within this run rather than repeatedly scanning unchanged files.
3. Inspect only necessary columns to confirm training/test date ranges, policy-row key, loss/report dates, exposure, incurred/recovery/status fields and sample columns. Check test row IDs for uniqueness and exact sample coverage. Sample predictions are placeholders, not labels.
4. Write the machine-specific inventory under outputs/step1/. Write a reviewed aggregate summary in docs/step1/data-readiness.md with discrepancies and explicit status. Do not commit local absolute paths or input records.
5. Treat reference audit anomalies as measured earlier, not newly reverified unless actually checked. A hash difference triggers reconciliation before relying on the old findings; never overwrite the reference manifest to make the check pass.
6. Document future requirements for exposure, IDs, linkage, recovery and maturity without executing those repairs here.

## Acceptance
File identities and required fields are established or discrepancies are reported. Train/test dates, 626,639 test rows and sample key coverage are verified on this machine. Raw hashes are unchanged after inspection. Next: Prompt 03.

---

## Prompt 03 — Specify target, exposure and assumptions

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Write the human-readable and machine-readable Step 1 contract. No developed labels or models.

## Deliverables
- docs/step1/problem-definition.md
- configs/problem_contract.json
- schemas/problem_contract.schema.json
- Updated docs/assumptions.md

## Required content
1. Prediction grain is row_id for a covered policy period. Eligible claims have the same line/policy and inclusive loss_date in [period_start, period_end], excluding declined/repudiated claims. Report/payment dates do not change that allocation. Claims outside supplied coverage are not forced onto another row.
2. Define expected total ultimate cost, separating claim frequency from severity and explaining why one policy's zero outcome does not invalidate a positive expectation.
3. State the net basis and avoid double subtraction of excess. Distinguish observed net incurred, unreported losses, development on reported claims, future recoveries and trend. Actual ultimate labels are not supplied.
4. Define row-period cost versus annual rate. Exposure is applied once. Date-derived inclusive ACT/365 is the audited candidate convention, with a later reversible correction. Do not perform correction here.
5. Document official fixed power 1.5, higher-is-better D², comparison with a null constant in standard sklearn semantics, and the distinction between that mathematical null and a practical training-only baseline.
6. Record competition pooling/weighting as provisional unless established. Scorer y_true mean for D² is a benchmark calculation, not a feature or training estimate. Do not use hidden test outcomes.
7. Submission contract: exact columns row_id/prediction; 626,639 rows; unique exact test IDs; finite numeric predictions; official minimum zero; separately documented strict positivity for local Tweedie compatibility. Sample order is a generation convention, not an invented official requirement.
8. Include source/status for every rule, remaining assumptions, approval state pending, and downstream scope exclusions. Schema must distinguish verified, proposed and unresolved fields; it must not force an unknown into a false answer.

## Verification examples
- A May 2025 loss reported February 2026 belongs to a January–June 2025 coverage row; a July loss does not.
- 10% probability times 1,000 CU yields expected cost 100 CU in the stated simple example.
- Annual expected cost 200 CU times exposure 0.25 yields 50 CU.
- 1,000 policies times 50 CU yields 50,000 CU, but equal totals can hide 10/90 CU risk-group differences.
- Model deviance 70 against null deviance 100 yields D² 0.3.

## Acceptance
JSON validates against the schema. Examples are explained correctly. Human review remains pending. Explicitly list the actuarial choices needing user review; do not invent answers or require approval for routine file edits. Next: Prompt 04.

---

## Prompt 04 — Implement and verify the metric contract

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Implement a small scoring utility using the documented standard implementation. Do not train a model or infer the competition's unknown weighting.

## Procedure
1. Read the contract and official sklearn documentation. Add src/iaa_hackathon/metrics.py with fixed-power-1.5 mean Tweedie deviance and D², plus explicit optional sample weights. Name the provisional pooling/weighting choice in reports.
2. Validate lengths, finite inputs, nonnegative targets, strictly positive predictions and valid weights. Do not silently floor values, change the power, swap y_true/y_pred or annualize row targets.
3. Specify and test the policy for all-zero/constant targets, zero total weight and too few rows. An undefined D² must be reported as undefined or raised clearly, never converted to a fabricated success score. Mean deviance can still be useful.
4. Add meaningful synthetic tests: empirical-mean null gives D² zero on nonconstant targets; perfect predictions on positive, nonconstant targets give one; a deliberately poor predictor is worse; invalid predictions are rejected; optional weighting is correct.
5. Use an independent arithmetic check: for p=1.5, deviance(y, mu)=4*(y/sqrt(mu)+sqrt(mu)-2*sqrt(y)). For y=[0,4] and mu=[1,1], mean deviance is 4. Compare this hand result with the utility. Do not merely test one wrapper against itself.
6. Demonstrate row-loss/rate equivalence if used: scaling both y and mu by exposure scales deviance by exposure^(2-p). For unweighted row loss at p=1.5, equivalent rate scoring uses sqrt(exposure) weights. Standard exposure-weighted rate fitting is a different objective. This is conditional on the scoring contract, not a new official fact.
7. Install only needed Step 1/dev dependencies. Record exact versions and the Python/platform context in a lock; exclude editable local absolute paths. Verify reinstallability in a fresh environment before claiming reproducibility. Update CI to run the actual metric tests.

## Acceptance
Independent arithmetic and behavioral tests pass. Undefined cases and provisional competition semantics are explicit. No real-data validation score is invented. Next: Prompt 05.

---

## Prompt 05 — Verify submission structure without generating predictions

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Implement the submission contract checker and synthetic tests. Do not create a competition prediction file.

## Procedure
1. Add src/iaa_hackathon/submission.py to validate a candidate frame/file against sample IDs and a declared contract. Separate official nonnegativity from optional strict-positive scoring compatibility.
2. Require exact two column names, expected row count, unique identifiers, exact ID coverage, finite numeric predictions, and no index column. Do not accept valid-looking M/B/C prefixes as a substitute for exact ID membership. Contents prefixes are C.
3. Permit IDs in a different order if the official contract does not require order, while providing sample order as the later generation convention. The displayed header's whitespace does not create a leading-space column name.
4. Add tiny synthetic fixtures/tests covering valid input; reordered IDs; missing/extra/duplicate IDs; wrong or extra columns; nonnumeric/NaN/infinite/negative values; and zero predictions under each declared positivity policy. Parameterize expected fixture rows rather than demanding 626,639 synthetic records.
5. Test CSV rereading so accidental index columns and identifier coercion are caught. Use synthetic records only.
6. Document how this checker will later be applied to the real sample. Do not derive predictions or claim an upload has been accepted.

## Acceptance
Behavioral tests establish the actual boundary rules, including zeros and ordering. No competition data or row-level output is staged in Git. Next: Prompt 06.

---

## Prompt 06 — Challenge the Step 1 contract

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Perform a skeptical review within this session, without spawning another agent or manufacturing human review.

## Procedure
1. Review the actual contract and tests against source evidence and what-good-looks-like.md. Try to find mistakes, not justify existing choices.
2. Challenge: loss versus report date; gross/net and double excess; future recoveries; policy period versus annual rate; applying exposure twice; unreported claims; incurred estimates versus final losses; right-truncated reporting patterns; and leakage through historical financial amounts.
3. Challenge scoring: fixed power; direction; null denominator; zero predictions; undefined D²; pooling/weights; and cases where aggregate calibration conceals segment mispricing.
4. Challenge status claims: original professional-standard citations are unverified; a card's existence is not proof; adjusted labels are not truth; an AI check is not human approval; a passing scaffold is not a completed Step 1.
5. Write docs/step1/challenge-review.md with each issue, evidence, severity, concrete action and resolution/status. Add a test only for a meaningful uncovered behavior. Fix clear in-scope defects and rerun affected checks.
6. Update assumptions and PROMPT_LOGS.md. Label this as AI review; human review stays pending. Do not require invented deployment or approval workflows.

## Acceptance
Every identified issue has a documented disposition. Remaining unknowns are visible and do not become confirmed facts. No unsupported accuracy or efficiency claims. Next: Prompt 07.

---

## Prompt 07 — Verify and hand over Step 1

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Provide a concrete, reviewable Step 1 package and a reliable one-command check.

## Procedure
1. Implement make step1-check to validate contract JSON/schema, execute nonzero behavioral tests, run synthetic examples and emit a concise verification summary. Fail if required modules/documents/tests are missing or if collection finds no tests. Separate this from local-data inventory verification.
2. Verify a fresh Python 3.12 environment can install the exact dependency lock and local package. Record actual commands and results. Avoid local absolute paths in the committed lock. State platform limits instead of promising universal byte identity.
3. Update CI with a Step 1 contract/test job that needs no raw data. Keep only read permissions. Verify the workflow's commands locally where possible; do not claim GitHub CI ran until it did.
4. Write docs/step1/acceptance.md mapping each objective to evidence: prediction grain; net basis; ultimate/reference distinction; exposure; fixed metric; submission identity; assumptions; and human decisions still needed.
5. Populate cards only with implemented facts. Update docs/status.md and PROMPT_LOGS.md. Machine verification can be complete while human actuarial acceptance remains pending.
6. Inspect git status/diffs and run the tracked-data check. Provide a suggested commit message and handoff summary. Do not commit, push or upload unless the user requests it.
7. Stop after Step 1. State the later work: actual cleaning, claim linkage/financial reconciliation, maturity modelling, split manifests, baselines and predictive training.

## Acceptance
make step1-check genuinely passes on synthetic data with tests collected. Contract and source evidence agree, remaining assumptions are explicit, and actual human acceptance has not been fabricated.

---
