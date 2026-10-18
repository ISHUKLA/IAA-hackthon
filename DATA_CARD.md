# Data Card — Step 3 claim/target status

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
