# S3-06 — Assemble development candidates without inventing outcomes

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

Objective: publish useful observed targets and conditional maturity candidates
while preserving exactly what is known and what is assumed.

1. Keep observed_net_incurred unchanged. Assemble each candidate from separately
   named reported-claim development, unreported net loss and future-recovery
   components. Include target version, financial-basis status, fit cutoff,
   assumptions, eligibility and provenance. Do not manufacture 2025 labels.
2. Prefer retaining reported counts, per-peril completeness/effective exposure
   and claim severity candidates as explicit inputs for later model choices.
   Do not force a monetary adjustment merely because a count factor exists.
3. An optional monetary inverse-reporting candidate is allowed only under
   documented assumptions about delay and net ultimate amount. For example,
   summing u_reported,j / q_j with q_j=F_k(cutoff-loss_date_j) over matched
   reported claims is a weighted proxy under conditional independence and
   positivity assumptions. It is not the realised hidden loss on that row.
   If amount depends materially on delay, a count CDF alone is insufficient.
4. For that candidate, reporting allowance is the difference between weighted
   reported net-ultimate cost and its unweighted counterpart. Do not also add
   a second cohort IBNR reserve. Future recoveries on unreported claims must
   already be reflected in their assumed net severity, not deducted twice.
   Do not silently cap weights; unsupported values require a documented
   alternative or an unavailable-candidate status.
5. Rows with no observed claims can remain zero in a sparse weighted proxy;
   that is not a declaration that they have no IBNR. Do not allocate hidden
   claims to specific policies or smear a portfolio reserve across all rows
   and then call that ground truth. Any alternative allocation must be separately
   declared and must not become its own independent validation evidence.
6. Reconcile components by row/peril/line/cohort and verify that full reporting,
   a=1 and no future recovery reproduce the observed reference. Ensure monetary
   targets remain period amounts; exposure is not applied twice. Record reference,
   reporting-only and supported scenario variants without selecting one by
   scoring against its own manufactured targets.
7. Full-snapshot diagnostic fits must be labelled accordingly. Export fit/transform
   interfaces and provenance so Step 4 can refit on permitted data; do not hand
   a full-data learned factor to a later fold as if it were leakage-free.

Acceptance: usable observed responses and transparent reserving outputs exist.
Conditional candidates are explicitly proxies. A definitive ultimate target
can remain unselected when the data cannot justify it. Next: S3-07.
