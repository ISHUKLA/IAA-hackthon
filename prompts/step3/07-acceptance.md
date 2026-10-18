# S3-07 — Verify, challenge and hand off to validation

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

Objective: provide reproducible claim/target construction and an honest maturity handoff.

1. Add make step3-check for nonzero synthetic tests of linkage, accounting,
   aggregation, delay likelihood/cutoffs, scenario identities and leakage/failure
   cases. Keep prior Step 1/2 checks passing. CI must require no competition data.
2. Add a full local command, such as make build-targets, using the Step 2 manifest
   and the target/scenario config. Write local crosswalks, quarantine tables,
   observed targets, completeness outputs, candidate scenarios and component
   reconciliations under outputs/step3/. Use atomic output publication and
   provenance for actual code/config/input versions, including uncommitted edits.
3. Verify row identity/count conservation, zero-row preservation, no duplicated
   claims, accounting identities and raw/clean input immutability. Same-hash,
   same-basis inputs should reconcile the reference totals; investigate rather
   than hard-code/relax discrepancies. Reruns must not reapply adjustments twice.
4. Challenge count-versus-amount completeness, truncated tails, calendar/mix
   changes, selected closed severities/recoveries, reserve releases, the extreme
   BI claim, model-dependent IBNR allocation, double adjustments and artificial
   historical financial snapshots. Fix in-scope defects; document remaining limits.
5. Write docs/step3/acceptance.md and the component-level aggregate report. State
   separately: deterministic observed-target readiness; delay-estimator evidence;
   scenario-engine verification; assumptions and human decisions still pending.
   A passing engine does not establish a financially correct selected scenario.
6. Update DATA_CARD.md, assumptions, status, the exact environment lock and
   PROMPT_LOGS.md. Report actual tests and numerical scenario impacts; do not
   fabricate actuarial sign-off, efficiency gains, ultimate accuracy or CI runs.
7. Hand Step 4 the observed targets, component/proxy versions, immutable manifests,
   estimator refit interfaces, cutoff rules and unresolved assumptions. Do not
   generate split manifests, tune pricing models or evaluate on fabricated
   ultimate labels as if they were independent truth. Do not commit or push.

Acceptance: deterministic outputs reconcile, synthetic and actual-data checks
are reported separately, assumptions remain visible, and the next phase can
compare models without silently inheriting full-data adjustment leakage.
