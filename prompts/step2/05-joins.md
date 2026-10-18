# S2-05 — Validate dimension and weather joins

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

Objective: prove that dimension enrichment preserves the policy-period grain.

1. Validate customers on customer_id, addresses on address_id, and weather on
   (address_id, year) at their required unique grains. Reject duplicate dimension
   keys instead of silently keeping the first record.
2. Implement/reuse guarded left joins, explicitly validating many-to-one
   cardinality and checking both row counts and the row_id multiset. A null key
   must not match another null key; pandas may otherwise do that. Preserve the
   policy row and record the missing reference.
3. Use cleaned customer references. For weather, derive the policy-period year
   only after checking the dates lie in one calendar year. If a period crosses
   years, flag a separate allocation decision rather than selecting the start
   year silently. Never join weather on address alone.
4. Check actual linkage completeness and no row multiplication across all six
   policy tables. Use explicit prefixes for overlapping dimension columns.
   Validate keys without creating a huge, unnecessary wide model matrix.
5. Test duplicate customer/address/weather keys, the same address in two weather
   years, missing/null foreign keys, reordered dimensions, duplicate policy IDs
   with distinct row_ids and a cross-year period. Correct joins must preserve
   policy rows, ordering convention, dates, premiums and exposure totals.
6. Claim interval linkage is Step 3. Do not allocate the 414 pre-coverage claims
   to arbitrary renewals, shift dates or construct a target during this prompt.

Acceptance: actual joins preserve grain and expected coverage; failure cases are
detected; weather-year semantics and unresolved exceptions are explicit.
Next: S2-06.
