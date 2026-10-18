# Prompt 03 — Specify target, exposure and assumptions

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
