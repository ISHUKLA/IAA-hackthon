# S2-07 — Challenge, acceptance checks and handoff

## Common instructions

Execute only this prompt. Preserve existing work, input files, Git identity
and Step 1 behavior. Use the current Python 3.12 environment and existing
inventory/scoring utilities where appropriate. Add only necessary dependencies
and extend the exact tested lock without gratuitous upgrades.

Use IAA_DATA_DIR or the explicitly supplied local data directory. Keep all
row-level cleaned files, exception ledgers and machine-specific reports under
ignored outputs/step2/. Commit only code, config, synthetic fixtures and
reviewed aggregate documentation. Do not copy raw data into the repository.

Make routine, reversible changes within scope without repeated permission
requests. Record genuinely unresolved decisions. Do not fabricate a human
approval, observed result, professional requirement or model score.

At the end report changed files, actual commands/results, before/after counts,
remaining issues and the next prompt. Update docs/status.md and PROMPT_LOGS.md.
Do not automatically run the next prompt. Do not construct targets, join
claims onto policy-period targets, estimate development, fit/tune models,
generate predictions, commit or push.

## Prompt-specific instructions

Objective: establish the Step 2 evidence and provide a usable handoff to Step 3.

1. Review transformations skeptically within this session, without spawning
   agents. Challenge ID collisions/nulls, date boundaries/leap days, denominator
   choice, inferred unit rules, duplicate dimension joins, missingness, unintended
   label/feature leakage, source modification and repeated execution.
2. Add make step2-check for meaningful synthetic behavior/invariant tests with
   nonzero test collection and no raw-data dependency. Keep make step1-check
   passing. Configure a raw-data-free CI job using the actual tested lock;
   do not assert that GitHub CI ran merely because a workflow file exists.
3. Separately verify full local acceptance through make prepare-data and its
   reconciliation. Require unchanged policy-row identity/counts, complete
   expected corrected joins, reconciled ACT/365 exposures, unchanged test
   exposures, retained missingness, visible sum-insured candidates, unchanged
   raw hashes and no prohibited Git-tracked records.
4. For unchanged source hashes, reconcile actual metrics with the reference
   table. Do not hard-code counts into functions, weaken checks or silently
   adjust expected values to pass. Document any legitimate difference.
5. Write docs/step2/acceptance.md and an aggregate cleaning report. Update
   DATA_CARD.md, assumptions, status and PROMPT_LOGS.md with actual results.
   If sum-insured adoption still needs human judgement, show the specific
   candidate impact and keep that item pending; do not falsely claim approval.
6. Inspect the Git diff. Summarise what is ready, what remains uncertain and
   the source-preserving inputs for Step 3. Do not start target construction,
   IBNR, validation splitting or training; do not commit or push.

Acceptance: synthetic checks and real-data reconciliations are reported
separately. Rebuild behavior is evidenced, prior Step 1 behavior is intact,
and human review is distinguished from automated/AI checks.
