# S2-04 — Preserve missingness and flag questionable values

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

Objective: distinguish data-quality issues from model-specific preprocessing.

1. Profile missingness by source/line/year. Distinguish non-opt-in telematics
   absence from an unexpected missing opted-in score. Preserve the opt-in flag
   and missing values rather than assigning a genuine score of zero.
2. Preserve ordinary missing values and add selected useful indicators. Do not
   drop rows or fit medians, category frequencies, scalers, target encodings or
   distribution-based imputation across all years. Those belong inside later
   validation folds. Do not add an imputer simply to make all cells non-null.
3. Review numeric/date inconsistencies. A licensing age below 14 is only a
   plausibility flag in this fictional market; do not assert a legal minimum or
   replace values with 14. Record the evidence and preserve original values.
4. Record a feature-availability registry: customer_service_contacts quarantined;
   renewal_decision training-only; annual weather conditional availability;
   customer/history aggregates require timing evidence. Keep raw fields for audit;
   this registry must not claim the fields are validated prospective predictors.
5. Test structural versus unexpected missingness and preservation of policy rows,
   original values and unknown categories. Do not implement model features here.

Acceptance: missingness is explained rather than hidden; subjective plausibility
rules remain flags; no information is learned from a future validation fold.
Next: S2-05.
