# Step 2 clean-data plan and S2-00 preflight

## Execution update

S2-01 through S2-07 were executed on 18 October 2026 after this preflight plan. The implemented source-preserving pipeline, reviewed aggregate results and handoff are documented in the other files in this directory. The original plan below remains as the pre-execution record.

## Status and boundary

At S2-00, only preflight and policy design had been completed and no corrected row, cleaned table or ledger yet existed. That statement is historical: later Step 2 prompts produced ignored, reversible clean tables and a ledger while retaining the prohibitions below.

Human actuarial acceptance of the Step 1 contract and the proposed exposure convention remains pending. That does not prevent reversible preparation with raw fields retained and uncertainty recorded.

## Repository reconciliation

The checkout began this bootstrap clean at commit `1e4ce8f` on `main`, tracking `origin/main`. The repository is no longer unborn or unpushed: those statements in the Step 0 history describe the state when the starter was imported. The initial Step 1 commit was subsequently created and pushed. No GitHub CI result was inspected, so the workflow remains defined but externally unverified. The Step 2 guide, prompts, scope update and S2-00 artifacts are currently uncommitted and have not been pushed.

## Actual preflight evidence

| Check | Actual result |
| --- | --- |
| `make check` | Passed; Git index policy and Python compilation passed |
| `make step1-check` | Passed; 45 tests collected and passed in 4.30 seconds; contract/schema/examples passed; human review still pending |
| Data configuration | `IAA_DATA_DIR` unset; the documented local directory was passed explicitly |
| Doctor | Passed; 11 expected files present, zero missing |
| Before-run inventory | Status `ready`; all 11 row counts, column counts and SHA-256 hashes matched the unchanged reference manifest |
| Test identity | 626,639 combined test rows and 626,639 distinct non-null `row_id` values; exact sample coverage |
| Raw continuity | Pre/post size, nanosecond mtime and inode matched; reference hashes matched |

The machine-specific before-run manifest is `outputs/step2/preflight/before-source-manifest.json`. It is ignored and contains the absolute local data path; no absolute path or input record is recorded here.

## Source row baseline

| Source | Rows before | Rows after S2-00 | S2-00 changes |
| --- | ---: | ---: | --- |
| `policies_motor.parquet` | 979,968 | 979,968 raw reference | None |
| `test_motor.parquet` | 254,986 | 254,986 raw reference | None |
| `policies_buildings.parquet` | 707,726 | 707,726 raw reference | None |
| `test_buildings.parquet` | 184,155 | 184,155 raw reference | None |
| `policies_contents.parquet` | 721,617 | 721,617 raw reference | None |
| `test_contents.parquet` | 187,498 | 187,498 raw reference | None |

“After” means the unchanged raw source remains present; S2-00 deliberately did not create clean tables.

## Versioned correction policy

`configs/cleaning.json` is version `step2-cleaning-v1`. Every rule declares inputs, added output columns, row identity, reason, evidence/status, error behavior and required tests.

1. **Customer identifiers — planned deterministic repair after reference validation.** Preserve the original `customer_id` and copy it to `customer_id_raw`; derive `customer_id_clean` only for supported exact eight-character canonical references. Reject collisions, duplicate dimension keys, malformed values and fuzzy matching. The 98,110 training and 25,554 test motor repairs are prior-audit regression checks, not values to force.
2. **Exposure — planned deterministic derivation under a proposed convention.** Preserve dates and `exposure`, copy `exposure_raw`, and derive `exposure_clean` from inclusive covered days divided by 365 and rounded to four decimals. Classify matches, stored days, 360-basis values and unresolved differences. The convention and adoption remain pending human review; dates are never rewritten.
3. **Sum insured — inferred candidate only.** Preserve `sum_insured` and expose a separately named factor-of-1,000 candidate with status, reason and flag for buildings/contents. Diagnostic separators lie in observed gaps but are not coverage limits. No candidate becomes canonical in S2-00.
4. **Missingness/availability — audit and flags only.** Preserve nulls and original values. No imputation, learned encoding or across-year fitting is allowed. Contacts remain quarantined; renewal decision remains training-only; weather and history availability remain conditional.
5. **Dimension/weather linkage — guarded validation.** Customers, addresses and `(address_id, year)` weather must be unique at their own grains. Later many-to-one checks preserve the `row_id` multiset and prevent null-to-null matching. Claim interval linkage is not part of Step 2.

## Output and ledger contract

Later prompts will create six Parquet policy outputs under ignored `outputs/step2/data/`, one source at a time in source order. Original source columns retain their names and types. Added raw/clean/candidate/status columns are defined by `schemas/step2-clean-policy.schema.json`; line-specific original fields remain permitted. Dimensions and claims remain immutable references rather than redundant wide copies.

The ignored row-level ledger contract is `schemas/step2-cleaning-ledger.schema.json`. Each record contains:

- source file and `row_id` or entity key;
- affected field;
- canonical-text original and derived values, retaining null explicitly;
- rule ID/version;
- reason and evidence status; and
- change status (`unchanged`, `changed`, `candidate`, `exception` or `invalid`).

Future publication must be atomic and must include config/code provenance, source/output digests, reconciliation and an explicit exception ledger. Previous clean outputs can never serve as raw inputs.

## Processing sequence

- S2-01 validates and repairs customer identifiers without changing row grain.
- S2-02 derives and reconciles exposure from preserved dates.
- S2-03 produces the reversible sum-insured candidate and evidence.
- S2-04 profiles/preserves missingness and defines availability flags.
- S2-05 validates dimension and weather joins without claim allocation.
- S2-06 assembles the deterministic local pipeline and reconciliation.
- S2-07 performs skeptical review and separates synthetic from real-data acceptance.

## Prerequisites and unresolved items

- S2-01 must verify the canonical customer-ID character pattern and uniqueness before padding; width alone is insufficient.
- S2-02 must remeasure exposure classifications/totals. Inclusive ACT/365 is still a proposed convention (A15), not organiser-confirmed truth.
- Sum-insured adoption remains an inferred candidate requiring human judgement (A04).
- Null-key behavior, dimension uniqueness, cross-year weather allocation and feature timestamps require later checks.
- The status terms `declined` and `repudiated`, financial-field accounting, maturity, recovery and scoring semantics remain outside this cleaning preflight.

Historical S2-00 handoff: S2-01 was next and was not executed automatically at that time.
