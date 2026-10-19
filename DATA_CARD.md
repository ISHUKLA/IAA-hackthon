# Data Card — current repaired Part 1 reference and history

## Current authoritative layer — Steps 2 repairs through 10

Current modelling consumes only outputs/step2/repairs, not the old raw-claim Step 3 target universe. It preserves 2,409,311 training/626,639 test policy rows, separately retains raw and derived fields, repairs 123,664 motor references and 14,229 training exposures, and exposes 2,797 train/730 test inferred SI repairs. Exact non-claim-ID equality removed 604 duplicate copies, leaving 162,546 clean claims: 162,133 matched, 413 quarantined. Accepted open/closed claims number 160,432 and reconcile to 741,156,868.43 CU under the provisional incurred-less-recorded-recoveries interpretation. Test exposure is unchanged.

Step 4 repaired response/reporting views and recovered frozen membership share this claim universe. S5–S9 use the explicitly named `repaired_observed_net_incurred_snapshot_2024-12-31`, not true ultimate. Step 10 rehashes raw/repaired identities, preserves the frozen file/models and adds aggregate region/BI/subsidence review only. Raw files, row ledgers, claims, model tables and predictions remain outside Git. The complete current narrative is docs/part1/methodology.md and limitations-and-assumptions.md; exact hashes are in configs/final_model.json and the local Step 9/10 manifests.

Human adoption of ACT/365, SI units, deduplication/quarantine and financial basis remains pending. One end-2024 valuation does not identify monetary IBNR, ultimate case adequacy, future recoveries or trend. Current data terms remain unverified. This card is evidence navigation, not approval or professional compliance.

## Historical stage descriptions below

The following earlier records are retained for audit continuity. In particular, the 744,330,677.04 CU raw-claim Step 3 total is NOT the repaired modelling response and must never be mixed with it.

## Provenance and identity

The local Part 1 inputs are eleven Parquet files kept outside Git. On 18 October 2026, the read-only inventory matched every schema size, row/column count and SHA-256 digest in `docs/evidence/expected-manifest.json`. Detailed machine-specific evidence is ignored under `outputs/step1/`; aggregate evidence is in `docs/step1/data-readiness.md`.

The three test tables contain 626,639 unique, non-null `row_id` values in total, with exact sample-submission key coverage. Training policy dates lie in 2021–2024 and test dates in 2025. Required policy exposure/date fields and claim loss/report/incurred/recovery/status fields exist.

## Intended Step 1 use

The verified fields support a contract for one expected net ultimate row-period cost per `row_id`. Raw data is read-only. No input records are committed, and Step 1 does not clean data, link claims, build a target, estimate maturity or train a model.

## Step 2 derived policy layer

Step 2 adds six machine-local, Git-ignored policy tables without overwriting source columns. The layer preserves all 3,035,950 policy rows and exact row ordering; adds verified customer-ID repairs, separately derived ACT/365 exposure, inferred but unadopted sum-insured candidates, missingness/plausibility flags and customer/address/weather linkage statuses. All dimension links are complete after supported ID normalization. Written-premium totals and all eleven raw file hashes are unchanged.

The rebuild command, content/code provenance, aggregate reconciliation and row-level ledger are documented in `docs/step2/`. The row-level outputs remain under ignored `outputs/step2/` and must not be committed.

## Known limitations

Actual ultimate labels are not supplied. The prior audit identified exposure, identifier, sum-insured, linkage, recovery, maturity, leakage and weather-timing questions; those findings apply to the matching file identities but were not all recomputed in Prompt 02. Financial field interpretation, correction rules and as-of feature availability require later reconciliation and human review. This card records implementation status; its existence is not proof of data quality or professional compliance.

The mechanical exposure reconciliation is complete, but human adoption of ACT/365 remains pending. The factor-of-1,000 sum-insured values remain explicitly inferred candidates pending human judgement. Customer-service contacts are quarantined, renewal decision is training-only, and weather/history availability remains conditional. Step 2 did not allocate claims, create targets, estimate development, build splits, train models or generate predictions.

## Step 3 local target layer

Step 3 links 162,736 claims to exactly one training policy period using inclusive loss dates and quarantines 414 pre-coverage claims; no ambiguous matches exist. Under the provisional gross-of-recorded-recoveries interpretation, 161,029 matched closed/open claims produce 744,330,677.04 CU observed net incurred across all 2,409,311 training rows. This is an observed 31 December 2024 snapshot, not realised ultimate.

Per-line/peril right-truncated geometric delay fits and effective reported exposure are diagnostic and full-snapshot, not fold-safe. A separate scenario engine exposes neutral, reserve-release and reserve-strengthening cases without selecting one or fabricating IBNR. Financial basis, future recovery, case adequacy, and final target adoption remain pending. The 78 MB row-level bundle is ignored under `outputs/step3/`; only aggregate documentation and reusable code belong in Git.
