# Conditional ultimate-cost experiment — 19 October 2026

## Decision and meaning

**Experimental, not promoted, not uploaded.** The original S9 CSV, models and manifest are unchanged. This separate candidate moves beyond unadjusted incurred by adding an estimated monetary unreported-claim component. It is a prediction of ultimate cost **conditional on explicit assumptions**, not a measured ultimate label, independent actuarial approval, or a demonstrated leaderboard improvement. The official [Data page](https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/data) confirms paid amounts already net excess, defines incurred as paid plus current case estimate, maps repudiated to declined, and distinguishes incurred from final ultimate. It does not prove whether recorded recoveries are already netted from incurred or whether case estimates are adequate.

For a policy row, the new response is:

`observed_net_incurred + sum_peril(exposure_clean × mature_peril_cost_rate × (1 − reporting_completeness_at_2024-12-31))`.

The peril cost rate is the 2021–22 accepted claim cost reported by a declared training cutoff divided by that cohort's reporting-adjusted exposure. The reporting completeness is the existing right-truncated geometric fit, separately fitted at the F2023/F2024 training cutoffs or end-2024 for the full refit. This is a Bornhuetter–Ferguson-style expected IBNR allocation. It does not identify which specific policies will have unreported claims. The same S6 compact Tweedie GLM features and settings, including exposure applied exactly once, were retained. No case multiplier, future-recovery or cost-trend adjustment was selected.

## Actual results

| Quantity | Result |
| --- | ---: |
| Repaired 2021–24 policy rows | 2,409,311 |
| Observed net incurred at end-2024 | 741,156,868.43 CU |
| Estimated unreported cost | 31,458,045.47 CU |
| Conditional response total | 772,614,913.90 CU |
| Motor bodily-injury share of estimated IBNR | 24,310,435.26 CU, about 77% |
| 2025 sample-order prediction rows | 626,639 |
| 2025 conditional-candidate total | 198,365,721.60 CU |
| 2025 totals: motor / buildings / contents | 113,990,416.73 / 66,862,990.74 / 17,512,314.13 CU |

The new CSV is ignored by Git at `submissions/part1_conditional_ultimate_bf_v1_d1c272ab2f55e4d0.csv`; its SHA-256 is `be022f970fd8ba7fd5842d980b8741f6c6e516b12d74942fbac2277a4ac17bc6`. It passed exact sample coverage/order, numeric-domain, line count/prefix, exposure-once and saved-model reload checks. It is **not** a chosen final entry.

| Frozen comparison, scored on the newly constructed conditional response | New GLM D² | Frozen S6 D² | New A/E |
| --- | ---: | ---: | ---: |
| F2023, 626,355 rows | 0.126534 | 0.126543 | 1.066354 |
| F2024, 626,190 rows | 0.139547 | 0.139377 | 1.045637 |

The primary comparison is slightly worse and the reused challenge slightly better. These scores have a **different, partly modelled response** from historical S6 scores and cannot be treated as independent evidence of true-ultimate accuracy or compared directly with Kaggle's hidden score. The constructed response adds an expected IBNR amount even to rows with no reported claims, which also changes the deviance distribution.

## Material limitations and open decisions

- The single end-2024 financial snapshot gives neither paid/case histories nor realised final claim costs. The monetary fold comparisons are retrospective; 2024 cannot be called a mature independent ultimate holdout.
- Reporting-delay fits have count follow-up evidence, not monetary completeness proof. Stable 2021–22 cost rates, the geometric tail and equal expected severity for reported/unreported claims within peril are assumptions. Observed older-cohort delay/severity patterns suggest this can be wrong, especially in bodily injury.
- The 2024 motor bodily-injury observed rate is 105.13 CU/exposure; the conditional IBNR bridge raises it to about 209.97, still below 2021/2022 observed rates of 244.64/237.62. This could reflect case development, cohort mix, severity drift or model error. No extra case factor is inferred from that difference.
- `incurred_to_date − recoveries` remains a provisional financial basis. Paid amounts already net excess, so excess is not subtracted again. Future recoveries, case adequacy and 2025 cost trend are unquantified, not assumed known to be zero.
- Human adoption of exposure and sum-insured repairs, the financial basis, maturity assumptions and final candidate is pending. The page currently shows invitation-required participation. No terms were accepted and no CSV was uploaded.

## Reproduce and verify

Run from the repo root with the tested Python, setting `IAA_DATA_DIR` to the original local public-data directory:

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python scripts/run_conditional_ultimate.py --data-dir "$IAA_DATA_DIR" --output-dir outputs/conditional-ultimate-recheck
```

The command refuses to overwrite an existing output directory. It checks frozen upstream hashes and model configuration, repaired claim/policy reconciliation, frozen F2023/F2024 membership, training-cutoff reporting fits, model convergence, saved-model reload equality and exact official-sample CSV coverage. If the same config and inputs reproduce the same 2025 values, the existing content-addressed CSV is reread and verified instead of rewritten. Row-level responses/predictions, fitted models and the CSV stay outside Git. The executed initial run used `outputs/conditional-ultimate-v1/`; its machine-readable details are in `summary.json`. After the code/tests above were added, all **191 tests passed**; no independent ultimate truth or human review was manufactured.

`make verify-submission` also passed on the unchanged historical Step 9 CSV. `git diff --check` passed and Git exclusions correctly ignore the new model output and CSV. The broader `make check` currently fails because the already tracked, unchanged `reports/d2_summary.csv` violates its no-tracked-CSV policy. That unrelated pre-existing file was preserved; this is an unresolved repository hygiene check, not a conditional-model test failure.
