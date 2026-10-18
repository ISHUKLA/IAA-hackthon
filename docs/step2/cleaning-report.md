# Step 2 aggregate cleaning report

## Build result

The local `prepare-data` command processed one source table at a time and wrote six source-preserving Parquet tables, one row-level ledger, a manifest and reconciliation report beneath ignored `outputs/step2/prepared/`. Publication is atomic. The bundle is approximately 117 MB and is not Git-tracked.

| Measure | Actual result |
| --- | ---: |
| Policy rows before and after | 3,035,950 / 3,035,950 |
| Motor customer-ID repairs | 123,664 |
| Training exposure corrections | 14,229 |
| Test exposure corrections | 0 |
| Sum-insured inferred candidates | 3,527 |
| Row-level ledger entries | 144,580 |
| Unresolved customer/address/weather links | 0 |
| Cross-year policy periods | 0 |

All original policy columns and exact `row_id` order were preserved. Written-premium totals match before and after for every source. Claims and dimension files were referenced but not transformed; no claim financial field, date, recovery or status was changed.

All eleven source hashes matched the reference before and after each full run. Repeated builds produced the same nonvolatile logical-output digest: `53badc0b97216a09ea005c5eb960d1196176e9180c0503360f6ba21c20470b36`. The manifest records the content digest of uncommitted code/config instead of implying that the current Git commit contains these edits.

The sum-insured field remains a candidate, not an adopted canonical correction. ACT/365 is exposed separately from the raw field and awaits human convention review. No target, claim allocation, IBNR estimate, split, trained model or prediction was created.

