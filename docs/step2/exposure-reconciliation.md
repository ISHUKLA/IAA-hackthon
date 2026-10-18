# Step 2 exposure reconciliation

## Implemented derivation

`exposure_raw`, `period_start` and `period_end` are preserved. `exposure_clean` is derived afresh as inclusive covered days divided by 365, rounded to four decimal places. The absolute comparison tolerance is 0.00005. A valid 366-day period is therefore 1.0027 and is not capped; 2024 periods retain their supplied 30 December maximum end date.

Rows are classified as `matches_act365`, `stored_day_units`, `stored_360_basis`, `unresolved_mismatch` or `invalid_dates`. Missing/inverted dates or unexplained mismatches fail the preparation command rather than being silently repaired.

## Actual reconciliation

| Source | ACT/365 | Day units | 360 basis | Unresolved | Raw total | Clean total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Motor train | 974,232 | 934 | 4,802 | 0 | 1,058,509.6812 | 787,157.5563 |
| Buildings train | 703,544 | 656 | 3,526 | 0 | 789,403.9271 | 590,560.1951 |
| Contents train | 717,306 | 729 | 3,582 | 0 | 810,722.5688 | 590,859.3077 |
| Motor test | 254,986 | 0 | 0 | 0 | 199,983.6004 | 199,983.6004 |
| Buildings test | 184,155 | 0 | 0 | 0 | 150,243.9088 | 150,243.9088 |
| Contents test | 187,498 | 0 | 0 | 0 | 150,123.7728 | 150,123.7728 |

The three training tables contain 14,229 explained differences: 2,319 stored-day rows and 11,910 360-basis rows. Test exposure remains unchanged at the value level. Year-level counts and totals are retained in the ignored reconciliation report.

Inclusive-day, leap-day, 366-day, day-unit, 360-basis, unchanged, invalid, unresolved and rerun behaviors are covered by synthetic tests. Human adoption of ACT/365 as the downstream canonical exposure remains pending even though its computation and reconciliation are verified.

