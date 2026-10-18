# S3-00 — Preflight and target-construction specification

## Common instructions

Execute only this prompt. Read the current AGENTS.md, the Step 1 contract,
Step 2 manifest/config and relevant evidence. Keep raw data and prior clean
outputs immutable. Use the existing Python 3.12 environment and utilities;
add only required dependencies and retain an exact tested lock.

All claim-level, policy-level target, exception and scenario outputs belong
under ignored outputs/step3/. Commit only code, configuration, genuinely
synthetic fixtures and reviewed aggregate documentation. Preserve row identity.

Separate measured facts, estimates, explicit assumptions and pending decisions.
Do not fabricate future payments, historical financial snapshots, unreported
claim records, actuarial approval or validation results. Perform ordinary
reversible work without repeated permission requests; ask only for a genuinely
missing decision required to adopt a final assumption. Continue useful work
that does not depend on that decision.

Do not train pricing models, create validation splits or test targets, tune
to a public leaderboard, generate competition predictions, commit or push.
Use synthetic tests for behavioral contracts and actual-data reconciliations
for data acceptance. Report them separately. Do not spawn subagents.

Finish with changed files, actual commands/results, reconciliations, remaining
limitations and the next prompt. Update status and PROMPT_LOGS.md truthfully.
Never turn AI review or machine tests into human approval. Do not automatically
run the next prompt.

## Prompt-specific instructions

Objective: establish valid local prerequisites and the exact target components.

1. Read AGENTS.md, context.md, what-good-looks-like.md, the latest source
   register, problem contract, Step 2 cleaning configuration, acceptance and
   output manifest. Inspect local Git state. Reconcile stale status statements.
2. Run the implemented Step 1 and Step 2 synthetic checks. Verify the full-data
   Step 2 manifest, source identities and clean row sets. Do not accept the mere
   presence of a report as proof. If local Step 2 outputs are absent, identify
   that exact prerequisite; prepare the Step 3 specification and source review
   without fabricating outputs or silently redoing all of Step 2.
3. Identify actual claims fields: claim_id, policy_id, line, peril, loss_date,
   report_date, status, paid_to_date, incurred_to_date and recoveries. Verify
   types, identifiers, statuses, report/loss chronology and the valuation cutoff.
4. Write configs/target_construction.json and docs/step3/target-plan.md. Specify
   coverage linkage, disjoint exception classes, financial basis, precision,
   reported-count definitions, component names and provenance/status fields.
   Resolve field meanings from official documentation where possible. If
   whether incurred already nets recoveries is ambiguous, show the competing
   interpretations; do not silently choose by which gives a nicer score.
5. Distinguish observed net incurred, reported-claim development, unreported net
   losses, future recoveries on reported claims and optional trend. Preserve
   the incurred-minus-observed-recoveries audit reference as provisional where
   necessary rather than falsely certifying its financial interpretation.
6. Define APIs with explicit fit populations and report/as-of cutoffs so later
   validation can refit estimators without using held-out outcomes. Full-snapshot
   estimates must be marked full-snapshot, not represented as fold-safe.

Acceptance: local prerequisite status and target schema are explicit; missing
inputs or source ambiguity remain visible. No ultimate labels are invented.
Next: S3-01.
