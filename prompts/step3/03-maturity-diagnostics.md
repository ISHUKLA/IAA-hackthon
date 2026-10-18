# S3-03 — Diagnose maturity and what can be identified

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

Objective: identify where and why the observed reference may differ from ultimate.

1. Calculate reporting delay = report_date - loss_date and maximum observable
   delay = valuation_date - loss_date. Report invalid/negative dates and reports
   after the valuation cutoff rather than accepting future observations.
2. Build count-only accident/reporting period tables and diagnostics by line,
   peril, loss cohort, claim age and status. Report counts, open shares, paid,
   incurred, case amounts, recoveries and tail concentration. Use denominators
   consistently: open-claim count share differs from open incurred share.
3. Explain right truncation: claims with reporting delay longer than their
   observable age are missing. An empirical CDF of observed delays is a diagnostic,
   not an unbiased reporting-completeness factor. Prioritize BI and subsidence;
   examine material case reserves on other perils too.
4. Explore severity/lag and recovery/settlement associations while stating their
   selection and maturity biases. Lower recent-year mean severity and a high
   open share do not identify the case-reserve uplift needed.
5. State the data limitation: there is one financial snapshot, no historic paid/
   incurred transaction triangle and no later financial outcome for today's
   open claims. Do not infer close dates or fabricate past case reserves.
6. Write docs/step3/maturity-diagnostics.md and an identification register:
   measurable, estimable under explicit assumptions, and not identified here.
   Keep large-loss sensitivity separate from deleting/capping the source loss.

Acceptance: maturity priorities and their evidential limits are explicit;
reporting, case adequacy and recoveries have not been conflated. Next: S3-04.
