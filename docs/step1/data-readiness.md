# Data readiness — Prompt 02

## Status

**Ready for contract definition, with later data treatments still unresolved.** A read-only local inspection on 18 October 2026 found all eleven expected Parquet files. Their row counts, column counts and SHA-256 digests exactly match `docs/evidence/expected-manifest.json`, whose reference audit is dated 17 October 2026. No discrepancy requires reconciliation before Prompt 03.

The detailed machine-specific result is `outputs/step1/data-inventory.json`. That ignored file contains the local absolute data path, runtime details, full schemas and full hashes. This reviewed summary contains no absolute local path and no input records.

## Checks performed

- The presence-only doctor found all 11 configured inputs.
- `pyarrow` 26.0.0 was installed in the ignored local environment. `pyproject.toml` now exposes only `pyarrow>=18` in a dedicated `inventory` extra; the broader modeling extra was not installed.
- The inventory opened Parquet metadata for every file, computed each SHA-256 digest once, and reused that digest for the manifest comparison.
- Only the required policy, claim and sample columns were loaded for date, type, null, key and coverage checks.
- Pre/post file size, nanosecond modification time and inode values matched for every input. Together with the single-run hashes matching the reference manifest, this establishes hash continuity without a redundant second scan. The command only opened raw inputs for reading.

## File identity

| File | Rows | Columns | Reference rows/columns/hash |
| --- | ---: | ---: | --- |
| `addresses.parquet` | 575,983 | 16 | Match |
| `claims.parquet` | 163,150 | 12 | Match |
| `customers.parquet` | 545,240 | 18 | Match |
| `policies_buildings.parquet` | 707,726 | 27 | Match |
| `policies_contents.parquet` | 721,617 | 28 | Match |
| `policies_motor.parquet` | 979,968 | 39 | Match |
| `sample_submission.parquet` | 626,639 | 2 | Match |
| `test_buildings.parquet` | 184,155 | 26 | Match |
| `test_contents.parquet` | 187,498 | 27 | Match |
| `test_motor.parquet` | 254,986 | 38 | Match |
| `weather.parquet` | 2,879,915 | 9 | Match |

## Required fields and ranges

All six policy tables contain non-null string `row_id` and `policy_id` fields, date32 `period_start` and `period_end`, and non-null double `exposure`. Every `row_id` is unique within its table. The three training tables have the same observed policy-date ranges: `period_start` 2021-01-01 through 2024-12-29 and `period_end` 2021-01-01 through 2024-12-30. The three test tables have `period_start` 2025-01-01 through 2025-12-30 and `period_end` 2025-01-01 through 2025-12-31. These extrema place all inspected policy dates inside the configured training and test years.

Training exposure ranges from 0.0027 to 365.0 in each line; test exposure ranges from 0.0027 to 1.0. These are observed extrema, not a conclusion that the raw exposure convention is valid. The earlier count and impact of exposure errors were not recomputed here.

`claims.parquet` contains non-null string `claim_id` and `policy_id`; date32 `loss_date` and `report_date`; string `status`; and double `incurred_to_date` and `recoveries`. The observed loss-date range is 2020-12-01 through 2024-12-29, the report-date range is 2021-01-02 through 2024-12-30, and the status values are `closed`, `open` and `repudiated`. No claim-to-policy linkage was attempted in this prompt.

## Test key and sample

The test tables contain 184,155 buildings rows, 187,498 contents rows and 254,986 motor rows: 626,639 rows in total. Their `row_id` values are non-null and unique both within tables and across the combined test set. `sample_submission.parquet` has exactly 626,639 unique, non-null keys and exactly the columns `row_id` and `prediction`; its key set equals the combined test key set with zero missing and zero extra keys. Every supplied prediction is zero. Those values are placeholders, not labels or evidence about ultimate cost.

## Earlier audit findings

Because all eleven current files are byte-identical to the reference manifest, the findings in `docs/evidence/known-findings.md` still refer to these file identities. This prompt did **not** independently recompute the earlier anomaly counts or financial impacts for motor customer-ID padding, exposure errors, sum-insured units, claim linkage exceptions, recoveries, claim maturity, large losses, suspect contacts, renewals or weather availability. They remain prior measured findings until a later scoped check reproduces them.

## Requirements for later prompts

- **Exposure:** preserve the raw field, define a separate inclusive ACT/365 earned exposure, flag discrepancies, and ensure exposure is applied exactly once. Do not repair it in place.
- **Identifiers:** preserve original identifiers and define any normalized motor customer ID as a separate derived field with reconciliation counts.
- **Claim linkage:** link by policy and loss date with inclusive policy-period boundaries; quarantine unmatched or ambiguous cases and retain an auditable reason. Report date must not replace loss date.
- **Recoveries:** keep observed incurred and recoveries distinct, confirm whether supplied incurred already reflects excess or recovery components, and prevent double subtraction. Model any future recovery separately from observed amounts.
- **Maturity:** retain the 31 December 2024 valuation basis, separate reported development from IBNR, and do not treat incurred-to-date or the immature 2024 holdout as guaranteed ultimate truth.

No data cleaning, target construction, reserving, model fitting or sample modification was performed. Next: Prompt 03.
