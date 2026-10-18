# S3-02 — Construct and reconcile the observed response

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

Objective: build a trustworthy observed reference before applying any development.

1. Resolve or explicitly qualify the monetary interpretation. Check paid versus
   incurred, case reserves, recovery treatment, excess and status exclusions.
   On the audited source, closed incurred equals paid and case amounts are
   nonnegative; those checks do not establish future reserve adequacy.
2. Under the declared gross-of-recoveries interpretation, observed net incurred
   is incurred_to_date minus recorded recoveries. Do not subtract excess twice.
   Exclude declined/repudiated claims explicitly and report unknown statuses.
   Keep paid, incurred, case and observed recoveries as separate source quantities.
3. Aggregate matched accepted claims by row_id and by row_id/peril. Left join
   back to every clean training policy row, preserving zero-claim rows, original
   row identity and corrected exposure. Count accepted reported claims separately
   from positive-cost rows; do not lose accepted zero-cost claims.
4. Reconcile source -> linkage groups -> status groups -> peril/line/year -> row
   response. Use a documented monetary tolerance consistent with source precision.
   Investigate negative net amounts; never clip, add an epsilon to labels or
   round claims solely to force reconciliation. Observed zeros remain valid.
5. Reproduce the three line totals and 744,330,677.04 CU combined reference if
   input hashes and interpretation are unchanged. Retain the 11.89m BI claim.
6. Test multiple claims/perils on one row, zero-claim rows, accepted zero amounts,
   repudiations, recovery subtraction, excess non-duplication and conservation.

Acceptance: all original training rows survive, financial totals reconcile and
the response is named observed_net_incurred, not actual_ultimate. Next: S3-03.
