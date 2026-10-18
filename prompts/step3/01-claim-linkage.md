# S3-01 — Link claims to loss-date coverage

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

Objective: assign each eligible source claim to its correct training policy-period.

1. Validate claim_id uniqueness and policy-period non-overlap within line/policy.
   Match claims.line and policy_id to the correct policy table, then require
   period_start <= loss_date <= period_end. Mid-term rows must stay distinct.
2. Produce a claim-to-row crosswalk with match count and disposition. Partition
   source claims into exactly-one-match, unmatched and ambiguous/multiple-match
   groups. Never silently drop duplicates or choose the nearest row.
3. Classify unmatched cases: unknown line/policy, before first supplied coverage,
   after last coverage, between periods, invalid date, or other explicit cause.
   Quarantine exceptions with their original amounts and dates. Do not shift a
   loss date or attach the 414 known exceptions to an arbitrary renewal.
4. Reconcile counts and monetary totals across the disjoint linkage groups.
   For identical audited inputs expect 162,736 single matches, 414 pre-coverage
   exceptions and no multiple matches. Verify rather than hard-code.
5. Test boundary dates, a next-year report for an in-period loss, mid-term changes,
   gaps, wrong line, unknown policy, overlapping periods and repeated claim IDs.
   Allocate by loss date; report/payment dates do not select the coverage row.
6. Keep claim outcome fields in the response-construction area. Do not promote
   them into pricing features or join them onto future test rows.

Acceptance: every source claim has a traceable disposition and all counts and
amounts reconcile; ambiguous matches cannot pass silently. Next: S3-02.
