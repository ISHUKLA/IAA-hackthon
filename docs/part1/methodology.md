# Part 1 methodology — frozen proxy specification

## Data and response

Eleven original Parquet inputs are read-only and outside Git. Current identities are pinned in `configs/final_model.json`; the repaired source layer is `outputs/step2/repairs/`. It retains 2,409,311 training rows and 626,639 test rows. Motor IDs use validated eight-character references, exposure is separately derived inclusive ACT/365 rounded to four decimals, and suspected x1000 sum-insured errors use a separately named inferred field. Exact non-claim-ID duplicates lose only duplicate copies, never unrelated claim fields. These decisions remain reviewable; raw values are not overwritten.

Claims match the same line/policy and an inclusive covered loss date, not report/payment date. There are 162,133 matched clean claims, 160,432 accepted open/closed claims and 413 quarantined unmatched claims. Accepted incurred less recorded recoveries reconciles to 741,156,868.43 CU. The provisional repudiated/declined mapping excludes zero recorded amounts. No additional excess deduction is made. Old raw-claim Step 3 totals of 744,330,677.04 CU refer to a different historical universe and must not be mixed with the repaired response.

Exact response: `repaired_observed_net_incurred_snapshot_2024-12-31`. Case factor one, no additional monetary IBNR/development/future-recovery allowance and trend factor one preserve the identity proxy. These are not actuarial estimates that future components are zero. See [limitations-and-assumptions.md](limitations-and-assumptions.md).

## Frozen model and features

Three Tweedie regressions use power 1.5, log link, alpha=1, Newton–Cholesky solver, tolerance=1e-5 and maximum 100 iterations. The exact 14 motor, 11 buildings and 13 contents features/derived blocks are pinned in `configs/final_model.json` and the frozen S6 benchmark. Motor retains age nonlinearity/missingness; buildings log insured/occupancy-security; contents log insured/household-use/security-value. Raw IDs, outcomes, status, contacts, renewal decisions, annual weather, telematics score, premium and financial histories are not predictors.

Numeric medians, missing indicators, scaling, categorical imputation and category vocabulary are fitted only on eligible same-line training rows. The response is period cost / clean exposure; fitting weights are square-root exposure, corresponding to the local power-1.5 period-cost deviance objective. Predicted annual rate is multiplied by clean exposure exactly once. There is no floor, clipping, economic minimum or calibration multiplier.

## Validation

F2023 trains 2021–2022 and scores 2023; it is primary. F2024 trains 2021–2023 and scores 2024; it is a reused recent-year development challenge, not an untouched final holdout. F2022 was an optional framework fold, not an extra final-model score claimed here. Membership digest `f444d8c7f7a91e842a5f2789d212121bb65578d4e1389ce5cf56f3f4eb1a7fa5` was recovered exactly after an earlier artifact decoding failure; original corrupt bytes were preserved.

All monetary responses are valued at end-2024, not each historical prediction boundary. Thus train-only feature processing and chronological membership do not turn these comparisons into fully prospective monetary or ultimate backtests. Pooling and scoring weights are provisional local unweighted policy-period choices; exact official implementation is unverified.

## Selection and authority

Compare B0 global mean, B1 line exposure rate, conditional B2 premium comparator, B3 compact GLM, then bounded S6 blocks on identical rows. S7 LightGBM did not improve primary criteria; additional configurations were skipped. S8 tested one preregistered contents coefficient and rejected it. S8 `retain_benchmark` governs S9 unchanged full refitting. The original brief's ensemble preference and page-one layout are preserved as historical user design directions, not silently re-labelled as human approval of the later conditional choice.

S9 saved/reloaded all three full-training GLMs; Step 10 reverified and reproduced them only to audit the frozen candidate. Regional and peril summaries are post-selection diagnostics, not new rating features or response adjustments. No model/target/feature change is made in Step 10.
