# Motor NCB/customer/region GLM challenge — 19 October 2026

## Scope and target status

The direct request was to add `ncb_years` to the motor GLM and test marital status, occupation, `prior_claims_5y` and region, on both folds with and without the 11.89M CU claim row. This is a separate challenger, not a change to frozen S6/S9 or an approved 2025 submission. It uses the same power-1.5 log-link Tweedie GLM, alpha 1, training-only preprocessing, square-root exposure rate weights and one multiplication by exposure at prediction. A one-field `driver_age` probe gives a like-for-like check of the claim that NCB alone is stronger; it is not the S6 benchmark.

The repaired motor policy table has 979,968 rows. `ncb_years` is in that table. `marital_status`, `occupation` and `prior_claims_5y` come from the supplied `customers.parquet`, joined by cleaned customer ID; `region` comes from `addresses.parquet`, joined by address ID. The dimensions have 545,240 and 575,983 complete unique keys respectively. Both guarded many-to-one joins covered every motor training row without multiplication or reordering. Frozen source/configuration identities and fold memberships passed preflight. The source dimensions have no historical versions or quote-time timestamps; in particular, `prior_claims_5y` cannot be assumed to be an as-of claim count for earlier folds. Its fitted scores are exploratory and it is **not eligible for quote-time selection** without a timing reconstruction.

The stored `ncb_exceeds_licensed_flag` exactly equals `ncb_years > years_licensed` on all motor rows. It flags 127,041 rows (12.96%); NCB has no missing values and ranges from 0 to 15. The flag is a data-quality diagnostic, not a model predictor or a silent deletion rule. F2023/F2024 validation contain 33,157/34,103 flagged rows. Interpretation of NCB greater than licensed years needs human/domain review before deployment.

## Fold comparisons

These are **motor-line**, unweighted policy-period Tweedie D² values, not all-line or official Kaggle scores. F2023 is the primary selection fold; F2024 is the previously reused recent-year challenge. “Without row” rescored fixed predictions after excluding the *entire* F2023 policy row containing the 11,894,276.93 CU accepted motor bodily-injury claim. All training and all primary scores retain the row. The specified row is not in F2024 validation, so F2024 “without” equals “with.” This differs from the older Step 6 sensitivity that subtracted only the claim amount while retaining its row.

| Candidate | Observed snapshot F2023 | F2023 without row | Observed snapshot F2024 |
| --- | ---: | ---: | ---: |
| Frozen S6 motor | 0.080257 | 0.062311 | 0.046627 |
| Driver age only | 0.056219 | 0.046059 | 0.025551 |
| NCB only | 0.069279 | 0.060604 | 0.042691 |
| S6 + NCB | 0.093289 | 0.075116 | 0.057878 |
| + marital status | 0.092169 | 0.075475 | 0.057934 |
| + occupation | 0.093065 | 0.075407 | 0.057986 |
| + prior claims | 0.093497 | 0.076987 | 0.059834 |
| + region | **0.094340** | 0.076445 | 0.059639 |
| + all four additional fields | 0.093390 | 0.078928 | 0.061855 |

| Candidate | Constructed conditional target F2023 | F2023 without row | Constructed conditional target F2024 |
| --- | ---: | ---: | ---: |
| Saved conditional S6 motor | 0.096198 | 0.076784 | 0.089092 |
| Driver age only | 0.067757 | 0.057474 | 0.062598 |
| NCB only | 0.082531 | 0.074196 | 0.079418 |
| S6 + NCB | 0.110901 | 0.091340 | 0.095083 |
| + marital status | 0.109543 | 0.091769 | 0.095128 |
| + occupation | 0.110583 | 0.091644 | 0.094712 |
| + prior claims | 0.111019 | 0.093480 | 0.097192 |
| + region | **0.112105** | 0.092896 | 0.097399 |
| + all four additional fields | 0.110775 | 0.095726 | 0.099355 |

NCB-only beats driver-age-only on both folds and both response versions, but neither univariate model beats the multivariable S6 baseline. Adding NCB to S6 improves the primary and challenge scores on both responses. Region adds a small further primary-fold gain (conditional D² 0.110901 → 0.112105; observed 0.093289 → 0.094340), and the challenge agrees. Marital status and occupation lower the primary all-row score relative to S6+NCB; the four-field bundle lowers it relative to NCB+region despite a higher F2024 score. Prior claims has a small primary gain but unresolved as-of timing, so no selection claim is made for it. A predeclared uncertainty interval was not available for these post-request exploratory comparisons; the small region increment should not be treated as statistically established.

On the observed snapshot, S6+NCB+region motor A/E is 1.075 in F2023 and 0.841 in F2024; on the constructed target it is 1.103 and 1.046. The 2024 observed underprediction/maturity problem is not fixed by these features. For NCB+region, the flagged/unflagged A/E pairs are 1.013/1.086 (F2023 observed), 0.860/0.838 (F2024 observed), 1.037/1.114 (F2023 conditional), and 1.046/1.047 (F2024 conditional). This is descriptive; no flagged-row coefficient, post-hoc calibration or adjustment was fitted.

## Decision, provenance and reproduction

The provisional feature finding is **retain NCB for further motor-challenger investigation** and treat region as conditional on address-vintage review. Reject marital status and occupation as incremental primary-fold improvements; quarantine `prior_claims_5y` until its as-of definition is established. Frozen production models and all existing 2025 files are unchanged. No new CSV was built or promoted from this experiment. Human actuarial approval remains pending.

The observed target is repaired accepted net incurred at the single 31 December 2024 valuation. The conditional target adds an assumption-dependent monetary IBNR estimate. Neither is realised ultimate, and their D² values are not comparable across target versions. The claim’s loss date determines the included policy period; the experiment does not invent additional case development, future recoveries or 2025 trend. There are no realised 2025 ultimate outcomes, hence **no 2025 D²**. Exact competition scoring weights/pooling are also unresolved.

Reproduce from the repository root using the original local public data directory and fresh ignored output paths:

```sh
PYTHONPATH=src .venv/bin/python scripts/run_motor_features.py --data-dir "$IAA_DATA_DIR" --output-dir outputs/motor-feature-observed-recheck --target observed
PYTHONPATH=src .venv/bin/python scripts/run_motor_features.py --data-dir "$IAA_DATA_DIR" --output-dir outputs/motor-feature-conditional-recheck --target conditional
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_motor_glm.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Actual local runs completed 16 converged fits per target across F2023/F2024, with exact saved-model reload predictions and ignored model/prediction/manifest artifacts in `outputs/motor-feature-{observed,conditional}-v1/`. Each manifest records the frozen configuration and source SHA-256 identities. The focused 5 tests and full 200-test suite passed; the only test warning was joblib's physical-core-count fallback in this sandbox. Python compilation, `git diff --check` and output exclusions passed. The unchanged Step 9 626,639-row snapshot-proxy CSV reverified at its existing SHA-256. `make check` still fails on the already tracked, unchanged `reports/d2_summary.csv`, which its index policy prohibits; that unrelated file was preserved. An initial `make verify-submission` call omitted the required `DATA_DIR` and failed before verification; rerunning with the original data path passed. The first conditional invocation failed before fitting because `period_end` was omitted from the runner's view; the script was corrected, its empty new output directory removed, and the complete run then passed. No raw data, prior code, older models or row-level outputs were modified; no commit, push or upload was performed.
