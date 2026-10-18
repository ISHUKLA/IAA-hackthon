# S2-00 — Preflight, correction policy and baseline

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

Objective: establish a bounded, reproducible Step 2 work plan from the actual checkout.

1. Read AGENTS.md, context.md, what-good-looks-like.md, docs/plan.md,
   configs/problem_contract.json, docs/step1/acceptance.md, current status,
   known findings and the reference manifest. Inspect git status and preserve
   unrelated changes. Reconcile stale empty/unpushed status statements with
   actual local Git state; retain genuine historical facts as historical.
2. Run make check and the implemented make step1-check. Report actual results;
   do not assume the earlier 45-test result is still current. Identify any
   prerequisite affecting exposure/identifiers. Missing human sign-off remains
   visible, but is not a reason to refuse all reversible preparation.
3. Resolve the data path. Reuse the inventory command and prior evidence where
   still valid. Establish the eleven source identities and a before-run manifest.
   Do not change the reference hashes to match different input files.
4. Write docs/step2/cleaning-plan.md and configs/cleaning.json. Specify each
   rule's inputs, output columns, reason/status, row identity, error behavior
   and tests. Separate deterministic repairs from inferred candidates.
5. Define output schemas and a row-level ledger: source file, row_id/entity key,
   field, original value, derived value, rule/version, reason and evidence status.
   Row-level ledgers stay ignored. Keep raw values and existing schema semantics.
6. Plan to process one line/split at a time. Prefer six clean policy tables and
   immutable references to dimension/claim files over redundant copies and
   unnecessarily wide model matrices. No imputation or learned transforms yet.

Outputs: cleaning config, plan, preflight evidence/status and agreed output schema.
Acceptance: scope and raw identities are explicit; Step 1 regressions are known;
no data correction has yet been performed. Next: S2-01.
