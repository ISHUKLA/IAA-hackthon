# Data Card — Step 1 status

## Provenance and identity

The local Part 1 inputs are eleven Parquet files kept outside Git. On 18 October 2026, the read-only inventory matched every schema size, row/column count and SHA-256 digest in `docs/evidence/expected-manifest.json`. Detailed machine-specific evidence is ignored under `outputs/step1/`; aggregate evidence is in `docs/step1/data-readiness.md`.

The three test tables contain 626,639 unique, non-null `row_id` values in total, with exact sample-submission key coverage. Training policy dates lie in 2021–2024 and test dates in 2025. Required policy exposure/date fields and claim loss/report/incurred/recovery/status fields exist.

## Intended Step 1 use

The verified fields support a contract for one expected net ultimate row-period cost per `row_id`. Raw data is read-only. No input records are committed, and Step 1 does not clean data, link claims, build a target, estimate maturity or train a model.

## Known limitations

Actual ultimate labels are not supplied. The prior audit identified exposure, identifier, sum-insured, linkage, recovery, maturity, leakage and weather-timing questions; those findings apply to the matching file identities but were not all recomputed in Prompt 02. Financial field interpretation, correction rules and as-of feature availability require later reconciliation and human review. This card records implementation status; its existence is not proof of data quality or professional compliance.
