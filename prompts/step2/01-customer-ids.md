# S2-01 — Repair customer identifiers safely

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

Objective: recover valid customer joins while preserving identifiers and row grain.

1. Confirm the canonical identifier format and eight-character width from the
   unique customers reference. Do not assume a numeric format without checking.
2. Implement a pure, null-safe normalization function for supported shortened
   motor customer IDs. Preserve customer_id_raw; add customer_id_clean and a
   changed/reason flag. Do not coerce missing values to 'nan' or 'None'. Do not
   convert IDs through numeric types or alter row_id, policy_id or address_id.
3. Reject or flag unsupported, overlong or malformed values. Confirm reference
   uniqueness; several policy references to one customer are valid, duplicate
   dimension keys are not. Do not invent customer records or fuzzy-match names.
4. Verify all six policy tables. On identical inputs, recover 98,110 train and
   25,554 test motor joins; home-line joins should already work. Report actual
   before/after counts, unresolved keys and normalization effects.
5. Add meaningful synthetic tests: leading-zero recovery, an already canonical
   value, nulls, malformed/overlong values, duplicate dimension-key rejection,
   allowed many-to-one policy references and repeat-application behavior.

Acceptance: policy row counts/IDs are unchanged; repaired reference joins are
complete or unexpected failures are visible; no dimension collision is hidden.
Next: S2-02.
