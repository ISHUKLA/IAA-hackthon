# Step 3 target-construction plan and implementation record

## Status and boundary

S3-00 completed prerequisite verification and the target-component specification on 18 October 2026. S3-01 through S3-07 subsequently implemented and verified the bounded linkage, observed-response, count-delay diagnostic and scenario work. No unreported monetary loss was invented; no final scenario was selected; no validation split, pricing model, test target or prediction was created.

The intended prediction remains expected net ultimate policy-period cost. The only immediately observable claim quantities are a single snapshot as at 31 December 2024. They are evidence for an observed reference, not realised ultimate outcomes.

## Local prerequisites actually checked

| Check | Actual result |
| --- | --- |
| Repository | `main` at `1e4ce8f`, tracking the unchanged `origin/main`; existing Step 2 work remains uncommitted and was preserved |
| Step 1 synthetic gate | Passed; 45 tests collected and passed |
| Step 2 synthetic gate | Passed; 24 tests collected and passed |
| Step 2 real-data acceptance | Passed for 3,035,950 policy rows, 123,664 ID repairs, 14,229 exposure corrections, 3,527 inferred sum-insured candidates and 144,580 ledger rows |
| Raw source identities | All eleven files freshly rehashed and matched the Step 2 manifest |
| Step 2 output identities | All six clean tables, the ledger and reconciliation file freshly rehashed and matched the manifest |
| Clean policy row identity | Each of the six clean `row_id` arrays exactly matched its raw source in value, order and row count; all were non-null and unique |
| Step 2 rebuild evidence | Manifest status complete; raw before/after hashes matched; repeated logical digest `53badc0b97216a09ea005c5eb960d1196176e9180c0503360f6ba21c20470b36` |

`IAA_DATA_DIR` remains unset, so the known local data directory was supplied explicitly for read-only checks. The Arrow runtime emitted nonfatal macOS sandbox cache-size warnings; every command exited successfully. No Step 2 output was regenerated or modified.

## Claim snapshot review

`claims.parquet` matches reference SHA-256 `323adf2e0f6c5975a026479d725d4cd04f51fce3aa069f897a99f664c6e392c0` and has 163,150 rows. The ten target-construction fields are present with these physical types:

| Fields | Type | Nulls |
| --- | --- | ---: |
| `claim_id`, `policy_id`, `line`, `peril`, `status` | string | 0 each |
| `loss_date`, `report_date` | date32 | 0 each |
| `paid_to_date`, `incurred_to_date`, `recoveries` | double | 0 each |

`claim_id` has 163,150 distinct values. Lines are motor 112,606, buildings 26,442 and contents 24,102. Statuses are closed 151,292, open 10,147 and repudiated 1,711. Eleven peril values were observed; no unrecognised line or status is silently accepted by the planned contract.

Loss dates range from 1 December 2020 to 29 December 2024; report dates range from 2 January 2021 to 30 December 2024. There are zero reports before loss, zero losses after the valuation date and zero reports after the valuation date. Source incurred is 773,731,129.10 CU, paid is 683,306,660.07 CU and recorded recoveries are 27,678,633.34 CU. All are non-null and nonnegative. The derived case balance `incurred_to_date - paid_to_date` is nonnegative for every row and totals 90,424,469.03 CU. Closed incurred equals closed paid on this snapshot. All 1,711 repudiated rows have zero paid, incurred and recoveries. These checks do not establish reserve adequacy or the financial basis of incurred.

## Coverage-linkage contract

S3-01 will validate claim uniqueness and non-overlapping policy periods, then match on exact `line` and `policy_id` with inclusive `period_start <= loss_date <= period_end`. Report date and payment information never choose the policy row. Every source claim must enter exactly one disjoint disposition: exactly one match, unmatched, or ambiguous/multiple match. Unmatched cases have explicit causes; multiple matches and duplicate claim IDs fail rather than being resolved by proximity.

The claim crosswalk retains original dates, status and amounts. Outcome fields remain in the response-construction area and are not pricing features. S3-00 created no crosswalk; the later atomic build writes the crosswalk and quarantine under ignored `outputs/step3/prepared/`.

## Financial basis and reported-count definitions

Official evidence establishes the goal as expected ultimate cost net of policy excess and recoveries and excluding declined claims. The available official source register does not establish whether `incurred_to_date` is gross or net of recorded recoveries, nor whether source paid/incurred already reflects all policy excess. Two interpretations therefore remain visible:

1. If incurred is gross of recorded recoveries, the provisional audit reference is `incurred_to_date - recoveries`.
2. If incurred is already net of recorded recoveries, the observed reference is `incurred_to_date`; another subtraction would double count recoveries.

No claim-level excess field exists. Policy excess must not be subtracted again without source evidence. The provisional incurred-minus-recoveries reference is retained because it is the prior audited basis, not because its interpretation has been certified or because it may produce a preferable score.

The local `repudiated` status is provisionally mapped to the official exclusion of declined claims while the terminology remains unresolved. Closed and open claims are accepted under the provisional status contract. Accepted reported claims are counted by unique claim ID regardless of positive cost; positive-cost claims are a separate measure. Unknown statuses fail reconciliation.

Source monetary values appear at two-decimal precision. Later reconciliation will validate conversion to integer minor units and preserve raw doubles; it will not round or clip to manufacture equality.

## Components and naming

The planned candidate identity is:

`observed_net_incurred + reported_claim_development_adjustment + unreported_net_loss_estimate - future_recoveries_reported_claims + trend_to_2025_cost_level`

Each component stays separate. Recorded recoveries are part of the pending observed-basis interpretation; future recoveries are a different, prospective quantity. Trend is disabled until explicitly supported. `observed_net_incurred` is a snapshot reference, not `actual_ultimate`. The observed component and three transparent reported-case variants are available locally; unreported monetary loss remains unavailable because count completeness alone does not identify amount completeness.

## Refit-safe API boundary

The planned APIs in `configs/target_construction.json` require an explicit as-of cutoff. Any reporting-delay fit records its fit population, fit-report cutoff, valuation cutoff, exclusions and peril grouping. A fit using all claims visible at 31 December 2024 is labelled `full_snapshot_diagnostic_not_fold_safe`. Later validation must refit from only its permitted claims and cutoff before transforming a held-out period; the full-snapshot artifact cannot be passed into a fold as though leakage-free.

The logical crosswalk and target schemas are `schemas/step3-claim-linkage.schema.json` and `schemas/step3-target-row.schema.json`. Row-level outputs, when implemented by later prompts, belong only under ignored `outputs/step3/` with atomic publication and content provenance.

## Missing prerequisites and unresolved decisions

- There is no missing local Step 2 artifact: hashes and row identities were directly reverified.
- The official/local evidence still does not resolve the incurred/recovery/excess accounting basis; A03 remains pending.
- The official term declined and local status repudiated have not been proven synonymous; A18 remains pending.
- Human adoption of ACT/365 and inferred sum-insured candidates remains pending. S3 uses the clean layer without turning those machine checks into approval.
- A single 31 December 2024 financial snapshot cannot identify ultimate case adequacy, future recoveries or unreported losses without assumptions.
- No historical financial transactions or later ultimate outcomes are available; no artificial snapshots will be created.
- Human actuarial contract and final-target review remain pending.

All Step 3 prompts are now executed under the user's later instruction to complete Step 3. Next: Step 4, only when separately requested.
