# S2-02 — Reconcile exposure to covered days

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

Objective: create a date-derived exposure and explain every difference.

1. Preserve dates and exposure_raw. Derive exposure_clean as inclusive covered
   days / 365, rounded to four decimals, matching the audited test convention.
   Validate non-null dates and period_end >= period_start. Invalid rows must
   fail/flag explicitly; do not silently drop them or invent dates.
2. Classify raw values as matching ACT/365, stored day units, a 360-day basis,
   or unresolved mismatch. Use declared numeric tolerances; do not simply flag
   exposure > 1. Preserve the classification and rule in the ledger.
3. Reconcile counts and exposure totals by source file, line and year against
   the reference table. Same-hash inputs should reproduce 14,229 exceptions.
   Test exposures should remain unchanged. Do not hard-code these results.
4. Do not extend 2024 coverage from the supplied 30 December end date to
   31 December. Do not force ACT/365 exposure to be at most one: a valid
   366-day period has exposure 366/365 under this convention.
5. Test one-day coverage, leap-day inclusion, valid 366-day coverage, day units,
   360-basis values, unchanged valid exposure, inverted/missing dates and reruns.
   Derive from preserved dates, never repeatedly scale a corrected number.

Acceptance: valid dates yield the declared exposure, corrections are explained,
source dates are unchanged and no unresolved mismatch is disguised as a repair.
Next: S2-03.
