# Step 2 prompt algorithm — clean and traceable data

Prepared 18 October 2026 for ISHUKLA/IAA-hackthon. This is an execution guide for your local coding harness, not a claim that cleaning has been implemented or run.

## Scope and starting evidence

Step 2 means the clean data layer in the revised plan: inspect, specify, repair, test and reconcile. Target construction, claim-to-period allocation, IBNR, reserving, validation splits, model fitting and submissions remain later work.

The current GitHub main tree contains the Step 1 contract, metric/submission code, an inventory command, tests and the environment lock. docs/status.md reports 45 passing tests and pending human actuarial acceptance. It also contains old statements about an empty/unpushed repository; those are stale relative to the files now visible on GitHub. The local checkout and actual command results take precedence over that stale execution status. This guide has not independently rerun the user's Mac tests.

Use the existing checkout, its .git directory and origin. Do not copy the original scaffold over the implemented Step 1 work. Read context.md then what-good-looks-like.md, followed by current evidence, contract and status. The user now requests Step 2; explicitly advance the current-scope paragraph in AGENTS.md without rewriting the historical Step 1 scope or inventing human approval.

## How to start without a missing-prompt loop

Save this document locally or attach it to the harness. The Step 2 prompt files do not have to exist yet. Paste this bootstrap instruction:

```text
Work in the existing ISHUKLA/IAA-hackthon checkout.

Read the supplied IAA_Step2_Prompt_Algorithm.md. If it is not attached,
read ~/Downloads/IAA_Step2_Prompt_Algorithm.md.

Read AGENTS.md and the current Step 1 status. This request authorizes
Step 2 preparation; preserve the existing repository and implemented work.

Copy this guide to PROMPT_ALGORITHM_STEP2.md. Create prompts/step2/
and write each numbered S2-00 through S2-07 prompt below to its stated
filename. Include the Common instructions in each file, so each prompt
remains usable independently. Preserve unrelated existing files.

Update only the current-scope paragraph of AGENTS.md to permit requested
Step 2 data preparation. Preserve the existing restrictions on training,
target development, publishing and fabricated human approval.

Then execute ONLY S2-00. Report the created files, actual checks,
unresolved items and the next prompt. Do not execute S2-01 automatically.
Do not commit or push unless I explicitly request it.
```

Run the remaining prompts one at a time. For example: `Read AGENTS.md. Execute only prompts/step2/01-customer-ids.md.` Review the result before proceeding. If a check fails, diagnose the current stage rather than changing expected counts to obtain a pass.

## Common instructions

These instructions belong in every numbered prompt:

```text
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
```

## Expected measurements for the identical audited inputs

These are regression checks from the earlier direct audit, not constants to force into transformation logic. Reverify file hashes against the existing reference. Different inputs or different results require an explanation.

| Repair | Expected previous finding |
| --- | --- |
| Motor customer IDs | 98,110 training and 25,554 test rows repaired; zero unresolved customer joins afterward |
| Buildings/contents customer joins | Complete already; no customer-ID changes expected |
| Motor exposure | 934 day-unit and 4,802 360-basis rows; clean total 787,157.5563 policy-years |
| Buildings exposure | 656 day-unit and 3,526 360-basis rows; clean total 590,560.1951 |
| Contents exposure | 729 day-unit and 3,582 360-basis rows; clean total 590,859.3077 |
| All exposure exceptions | 14,229 training rows; zero residual mismatches in the audited classification |
| Test exposure | No changes expected; totals motor 199,983.6004, buildings 150,243.9088, contents 150,123.7728 |
| Sum-insured candidates | Buildings: 1,395 train / 370 test; contents: 1,402 train / 360 test |
| Output policy rows | Motor 979,968 / 254,986; buildings 707,726 / 184,155; contents 721,617 / 187,498, training/test respectively |

The sum-insured factor-of-1,000 interpretation is an inference. Produce a clearly named candidate value and correction flag; do not silently turn it into organiser-confirmed truth. A pending review of that inference need not prevent deterministic ID/exposure work.

## S2-00 — Preflight, correction policy and baseline

Prompt file: `prompts/step2/00-preflight.md`

```text
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
```

## S2-01 — Repair customer identifiers safely

Prompt file: `prompts/step2/01-customer-ids.md`

```text
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
```

## S2-02 — Reconcile exposure to covered days

Prompt file: `prompts/step2/02-exposure.md`

```text
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
```

## S2-03 — Review the sum-insured unit cluster

Prompt file: `prompts/step2/03-sum-insured.md`

```text
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
```

## S2-04 — Preserve missingness and flag questionable values

Prompt file: `prompts/step2/04-missingness.md`

```text
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
```

## S2-05 — Validate dimension and weather joins

Prompt file: `prompts/step2/05-joins.md`

```text
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
```

## S2-06 — Assemble and reconcile the clean-data pipeline

Prompt file: `prompts/step2/06-pipeline.md`

```text
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
```

## S2-07 — Challenge, acceptance checks and handoff

Prompt file: `prompts/step2/07-acceptance.md`

```text
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
```

## Completion checklist

- Raw files unchanged; existing Step 1 behavior retained.
- Exactly the original six policy-row sets survive, including all 626,639 test rows.
- Motor customer links recovered without collisions or fabricated records.
- Exposure is inclusive ACT/365, corrected once, with counts and totals reconciled.
- Sum-insured candidates and uncertainty are retained; no silent claim capping.
- Missingness preserved; no globally fitted model preprocessing.
- Dimension/weather joins preserve row grain and reject ambiguous keys.
- Versioned cleaning config, ledger, manifest and aggregate report exist.
- Synthetic CI checks and full-data acceptance are separate and truthful.
- Human decisions still pending are explicit; no target, model or prediction is claimed.

## Primary implementation references

- Existing repository: https://github.com/ISHUKLA/IAA-hackthon
- pandas merge cardinality validation and null-key behavior: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
- pandas string padding: https://pandas.pydata.org/docs/reference/api/pandas.Series.str.zfill.html
- Competition source references and file fingerprints are already in docs/evidence/ of the repository. Use documentation for the installed, locked library version; do not upgrade merely to match the latest web documentation.
