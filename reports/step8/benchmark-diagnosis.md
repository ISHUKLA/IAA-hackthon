# Step 8 benchmark diagnosis

Date: 19 October 2026. Qualified benchmark: **S6 selected compact Tweedie GLM**. The completed S7 nonlinear comparison retained this model. Step 8 preflight passed 101 evidence checks and verified repaired input/claim hashes, the recovered frozen membership, S4 response-alias amount/exposure identities, S5–S7 versions, complete prediction coverage, reproduced scores, actual acceptance and artifact/code checksums. The earlier blocked reports/config are preserved in `reports/step8/history/pre-step7/`, and the blocked decision is preserved under ignored `outputs/step8/history/`.

Primary weakness selected before fitting: **contents underprediction at intermediate insured values on F2023**. Boundaries below are quantiles of 2021–2022 predictors, not bins learned from validation outcomes. The diagnostic and subsequent model comparison are exploratory on the primary fold; customer bootstrap intervals do not correct for this hypothesis selection.

| Training insured-quantile band | F2023 rows | Benchmark A/E | Customer-bootstrap 95% interval |
| --- | ---: | ---: | --- |
| 1 | 35323 | 1.0711298572819599 | [0.9652643014897253, 1.1591052745734813] |
| 2 | 35994 | 1.0052196879471405 | [0.9006888429023446, 1.1148696492786945] |
| 3 | 37224 | 1.1267034325670326 | [1.0306928906189359, 1.2394206240740007] |
| 4 | 38268 | 1.2071679337716243 | [1.0737723621513506, 1.321537348385097] |
| 5 | 40837 | 1.0337524406117216 | [0.9344536476146055, 1.1329883267960357] |

The third and fourth bands have A/E 1.1267/1.2072 and intervals above one, versus approximately 1.0052 in band two. Their insured boundaries are 33,200–43,500 and 43,500–57,600 CU. This is observed residual evidence, not proof that a curve feature is the cause or remedy. A single training-quantile curvature term is the minimum adequate test; the outcome and accounting basis stay fixed.

Pooled and line evidence:

| Fold | Scope | Benchmark mean deviance | Benchmark D² | A/E |
| --- | --- | ---: | ---: | ---: |
| F2023 | pooled | 103.49608782239278 | 0.11345157013436835 | 1.0499309465855395 |
| F2023 | motor | 120.7492256666021 | 0.08025650973866305 | 1.0353644589317161 |
| F2023 | buildings | 120.71310568539245 | 0.06125020062587405 | 1.0664407451683784 |
| F2023 | contents | 63.19437072682378 | 0.04568194498645772 | 1.0901257656601593 |
| F2024 | pooled | 99.43930802654187 | 0.08980138282838457 | 0.9088900586803975 |
| F2024 | motor | 108.63384331146969 | 0.0466271755419132 | 0.8034309705954918 |
| F2024 | buildings | 124.01118612127274 | 0.0566901016735023 | 1.0633389612673916 |
| F2024 | contents | 62.834458250770666 | 0.052262099399323914 | 1.0339037466968584 |

Benchmark calibration by prediction decile (observed snapshot totals divided by expected totals):

| Fold | Decile | Rows | A/E |
| --- | ---: | ---: | ---: |
| F2023 | 1 | 62636 | 1.0829440180317562 |
| F2023 | 2 | 62635 | 1.1163556559870214 |
| F2023 | 3 | 62636 | 1.0252397461542655 |
| F2023 | 4 | 62635 | 0.9872817253249849 |
| F2023 | 5 | 62636 | 0.9929079060398447 |
| F2023 | 6 | 62635 | 1.0370453881984623 |
| F2023 | 7 | 62635 | 0.9944767244014122 |
| F2023 | 8 | 62636 | 0.9714869143940729 |
| F2023 | 9 | 62635 | 0.9623190924497533 |
| F2023 | 10 | 62636 | 1.2134420836127722 |
| F2024 | 1 | 62619 | 1.2819783499997162 |
| F2024 | 2 | 62619 | 0.9709649731810918 |
| F2024 | 3 | 62619 | 0.9864003668147442 |
| F2024 | 4 | 62619 | 1.0338137745078986 |
| F2024 | 5 | 62619 | 1.0015498404783048 |
| F2024 | 6 | 62619 | 0.9629193626583532 |
| F2024 | 7 | 62619 | 0.9203444406190565 |
| F2024 | 8 | 62619 | 0.9046712626556409 |
| F2024 | 9 | 62619 | 0.893034896595737 |
| F2024 | 10 | 62619 | 0.8216560352204032 |

Benchmark exposure-band calibration:

| Fold | Exposure band | Rows | A/E |
| --- | --- | ---: | ---: |
| F2023 | (0.75, 1.0] | 439800 | 1.055192824129457 |
| F2023 | (-0.001, 0.25] | 68524 | 1.107661420865669 |
| F2023 | (0.5, 0.75] | 57910 | 1.0304617331468238 |
| F2023 | (0.25, 0.5] | 60121 | 0.9621635100800712 |
| F2024 | (-0.001, 0.25] | 68130 | 0.991879465539017 |
| F2024 | (0.75, 1.0] | 439674 | 0.9071886122652649 |
| F2024 | (0.5, 0.75] | 57582 | 0.8696468134210129 |
| F2024 | (0.25, 0.5] | 60804 | 0.9716444667873383 |

Benchmark scores on common-row tail diagnostics (the high-prediction mask in this table uses the candidate ranking):

| Fold | Tail | Benchmark mean deviance | Benchmark A/E |
| --- | --- | ---: | ---: |
| F2023 | top_1pct_observed | 3410.783312141453 | 44.32143936507055 |
| F2023 | excluding_top_1pct_observed | 70.08672182105654 | 0.3307421772055885 |
| F2023 | top_1pct_predicted | 170.37765880814743 | 1.1062384866875075 |
| F2024 | top_1pct_observed | 3019.5769460071015 | 38.795101848334895 |
| F2024 | excluding_top_1pct_observed | 69.94249244629019 | 0.30196253126473044 |
| F2024 | top_1pct_predicted | 152.73000635972795 | 0.7457320148345133 |

Large-loss and high-prediction-tail comparisons are diagnostics only. Observed-loss tail membership is unknown prospectively, so high A/E in that outcome-selected tail is not by itself a defect in the expected-cost model. The 11.89m CU motor BI loss remains in all primary comparisons. Motor and buildings predictions are copied bit-for-bit from the benchmark in this test; a contents-only refinement cannot quietly change those tails or add a reserve load.

Risk-dimension checks also cover driver-age training quantiles, buildings sum-insured quantiles, cover, occupancy, tenure, new/returning risks and missingness semantics in the frozen pipeline. The full 15 risk-band records, segment tables, reference-versus-predicted totals and loss cost per exposure are in `outputs/step8/diagnosis.json` and the experiment fold diagnostics. No row-level output is tracked in Git.

Stability and data-quality interpretation: F2024 was already inspected in S5–S7 and remains a reused development challenge. Its motor A/E is 0.8034 while buildings/contents exceed one. A single 31 December 2024 financial valuation cannot separate maturity, changing risk mix, financial definitions and model form. Deduplication, sum-insured and exposure hashes match the recorded repaired candidate; suspect contacts, weather, telematics score and unsafe financial/final-status history remain excluded. No new source correction or ultimate label was created.

The selected S6 GLM is readily interpretable and has verified saved-model reloads. Recorded S6 feature-experiment runtime was 61.88736547995359 seconds; benchmark-only peak memory was not measured. The S7 challenger added computation without establishing a stable primary advantage. This justified a restricted one-coefficient test rather than another broad nonlinear model.

Materiality was declared before the candidate fit. The prior S6-vs-S7 contents paired mean-deviance interval was [-0.33857580700467405, 0.06465582545756834]. Half its width, multiplied by the primary contents row share 0.2995841016675847, gives pooled gain threshold **0.060400893187577284**, equivalent to D² **0.0005173946005555436** on the fixed primary response. This is a conservative operational noise benchmark informed by an existing comparison, not a universal D² rule or a formal power calculation. The new paired interval must also have a positive lower limit, while the cost budget allows only one additional regression coefficient and two fits.


## Independent benchmark-ranked tail review

The acceptance review additionally evaluated high-prediction tails defined exclusively by the frozen benchmark. This was computed after the model decision as an independent reporting check; it did not inform the chosen candidate, gate or fit. The common-row table above uses the candidate-defined ranking and should not be confused with these benchmark-ranked tails.

| Fold | Benchmark prediction quantile | Rows | Benchmark mean deviance | Benchmark A/E |
| --- | ---: | ---: | ---: | ---: |
| F2023 | 0.99 | 6264 | 170.37765880814743 | 1.1062384866875075 |
| F2023 | 0.999 | 627 | 228.95046996495802 | 1.385529690733527 |
| F2024 | 0.99 | 6262 | 152.73000635972795 | 0.7457320148345133 |
| F2024 | 0.999 | 627 | 169.66195192770385 | 0.6960996188472601 |

Exact aggregates for both models on these rows are saved in ignored `outputs/step8/benchmark-tail-review.json` and reproduced by `make step8-acceptance`. Neither retrospective outcome-tail membership nor high predicted cost establishes a missing ultimate-development adjustment.
