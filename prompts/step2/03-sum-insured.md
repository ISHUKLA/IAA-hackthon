# S2-03 — Review the sum-insured unit cluster

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

Objective: produce an auditable correction candidate for the supported unit error.

1. Reverify distributions for buildings and contents separately. Prior diagnostic
   separators were 2 million CU for buildings and 1 million for contents. These
   lie in observed gaps; they are not coverage limits or universal correction rules.
2. Test the factor-of-1,000 explanation using divided-value plausibility and
   same-policy observations where available. Use training evidence to specify
   the rule; apply it consistently to test without using claims/outcomes.
   Sparse/new-business rows may lack policy history: record that limitation.
3. Preserve sum_insured_raw. Create sum_insured_candidate, unit_error_flag,
   proposed divisor/reason and status='inferred' where supported. Keep normal
   values unchanged. Flag ambiguous exceptions without arbitrary replacement.
   Do not silently overwrite the source field or claim a human approved the rule.
4. Reconcile candidate counts: 1,395/370 buildings and 1,402/360 contents in
   train/test for the audited inputs. Inspect exceptions and scaled distributions.
   Report evidence for the inference and what remains uncertain.
5. Test an ordinary value, a supported high-cluster value, nulls, an ambiguous
   boundary/new value, line-specific rules and reruns. Candidates always derive
   from the original value, so repeated execution cannot divide twice.
6. Do not extend the rule to claim amounts, written premiums or other fields.
   The 11.89 million CU bodily-injury claim must not be treated as a unit error
   merely because it is large. Continue other reversible work while review is pending.

Acceptance: a reversible candidate and clear review evidence exist; uncertainty
is preserved. Canonical downstream adoption remains an explicit decision.
Next: S2-04.
