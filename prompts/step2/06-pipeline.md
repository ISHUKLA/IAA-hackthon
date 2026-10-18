# S2-06 — Assemble and reconcile the clean-data pipeline

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

Objective: create a reproducible local preparation command from the verified rules.

1. Extend the existing CLI rather than replacing doctor/inventory. Add a command
   such as prepare-data and make prepare-data with explicit data-dir, output-dir
   and cleaning-config inputs. Reuse current modules; avoid a new framework.
2. Write six policy-table outputs with preserved row IDs, raw values, clean
   ID/exposure fields, sum-insured candidates and flags. Reference unchanged
   dimensions and claims through the input manifest. Keep all outputs and
   row-level exception/change ledgers under ignored outputs/step2/.
3. Process one source at a time. Use deterministic row ordering, explicit types,
   rule/config versions, input/output content hashes and actual environment/code
   provenance. Use a content digest when local code is uncommitted; do not imply
   a clean commit reproduces unrecorded edits. Publish completed outputs atomically
   so a failed run cannot leave a success manifest pointing at partial files.
4. Reconcile by file/line/year: row counts, exact row_id coverage, key uniqueness,
   exposure totals, missingness, corrections, candidate counts and join results.
   Preserve premium and claim financial fields. No source claim amount/status/
   date/recovery is altered; financial source totals remain unchanged.
5. Verify raw-input hashes before/after the preparation run without needlessly
   hashing every file in every earlier prompt. A changed input is a failure to
   investigate. Never rewrite raw files or reference fingerprints.
6. Rerun on the same inputs/config. Compare logical outputs, correction counts
   and nonvolatile content digests; timestamps need not match. Prove there is
   no double correction. Never read previous clean outputs as raw inputs.

Acceptance: one local command rebuilds all clean tables and a trustworthy
manifest/reconciliation report. Exceptions and inferred candidates remain visible.
Next: S2-07.
