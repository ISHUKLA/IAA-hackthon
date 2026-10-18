# IAA Part 1 — Consolidated implementation plan

Revised 18 October 2026. Planning document for approval; no predictive model has been trained and no validation or leaderboard result is claimed.

This combines the useful elements of the proposed approach with the direct data audit and the subsequent critical review. The objective is a useful, defensible three-line pricing workflow, with model complexity earned through evidence.

## 1. Verified starting point

Sources already read: context.md; what-good-looks-like.md; the official Kaggle overview, data description and rules; the uploaded approach; all eleven Parquet files. Current direct measurements take precedence over earlier summaries.

| Line | Training rows | Test rows | Zero observed-cost rows | Corrected training exposure, policy-years |
| --- | ---: | ---: | ---: | ---: |
| Motor | 979,968 | 254,986 | 89.99% | 787,157.56 |
| Buildings | 707,726 | 184,155 | 96.42% | 590,560.20 |
| Contents | 721,617 | 187,498 | 96.82% | 590,859.31 |

The response above is matched, accepted incurred cost less observed recoveries, not actual ultimate. There is no supplied ultimate target column. Total test rows are 626,639, matching the sample exactly. Identifiers are strings, dates date32, and rating variables are numeric, categorical or Boolean. Selected ordinary predictors have roughly 2.5–3% missingness; telematics-score absence is structural for non-opt-ins. The sample predictions are placeholders containing zero.

Verified defects and implications:

- Motor customer identifiers lost leading zeros. Eight-character padding resolves every failed join: 98,110 training rows and 25,554 test rows.
- 14,229 training exposures use day units or a 360-day basis. Inclusive covered days / 365, rounded to four decimal places, matches the clean pattern and every test exposure. Raw training totals are overstated by 34–37%.
- Buildings and contents have a separate high sum-insured cluster: 2,797 training rows and 730 test rows. A factor-of-1,000 unit error is a strong interpretation supported by repeated policies; it is not an organiser-confirmed fact.
- 162,736 claims match one coverage row; none match multiple rows. All 414 unmatched claims precede the first supplied coverage for their otherwise known policy. Quarantine and financially reconcile them.
- Recoveries total 27.68 million CU and equal 22.48% of motor own-damage incurred. Observed recoveries occur only on closed claims.
- Motor bodily injury and buildings subsidence need particular attention: their 2024 open shares are approximately 79.8% and 68.7% respectively.
- The largest incurred claim is an open motor bodily-injury claim of 11.89 million CU. Retain and investigate it; size alone does not demonstrate an error.
- Customer-service contacts have an extreme association with claims. This supports quarantine as suspected leakage, without proving their timestamp or the organisers' intent.
- Approximately 84.8% of test policies recur from training. Every test address has a supplied 2025 weather record.

## 2. Prediction and scoring contract

Predict the expected ultimate claim cost for each 2025 policy-period row, in the fictional currency, net of excess and recoveries and excluding declined claims. Predict period cost, rather than charged premium or an annual rate left unscaled.

The published metric is exactly: **“Tweedie D² score (power = 1.5)”**. Higher is better. It rewards accurate conditional means and calibration; systematic underprediction and very small predictions on positive losses are costly. Risk ranking alone is insufficient, and rare large losses still matter to the expected cost.

Official submission illustration:

```text
row_id, prediction
M02409311,583.47
B01834522,412.10
```

The actual sample column names are row_id and prediction. Generate a CSV with exactly those names and no index. The prose permits nonnegative predictions; strictly positive predictions are compatible with standard Tweedie implementations at power 1.5. Use a numerical safeguard if necessary, rather than automatically imposing a one-CU economic minimum.

Unresolved scoring assumption: use pooled, unweighted policy-period D² provisionally until the competition implementation establishes weighting and pooling. These details can affect training weights and model comparison.

## 3. Repair the data before estimating rates

Preserve the raw files and record each correction and its reason. Normalize motor customer IDs, rebuild exposure, and review the separated sum-insured cluster. Apply an approved unit rule consistently to training and test; retain original values and a correction flag. Do not infer thresholds from validation outcomes.

Keep supplied coverage dates, including the 2024 end-date convention. Validate many-to-one dimension joins and join weather on address plus year, not address alone. Review inconsistent age/licensing combinations without inventing a legal minimum in the fictional market.

Use an explicit unknown category and training-fitted numeric imputation for GLMs. LightGBM may retain missing values. Preserve telematics opt-in separately from score; structural absence is different from an accidentally missing measurement.

**Acceptance evidence:** unchanged policy-row counts; complete repaired customer/address joins; no join multiplication; every exposure reconciles; corrections reversible; before/after financial and exposure totals retained.

## 4. Construct the observed response and an explicit maturity bridge

Link claims by line, policy and inclusive loss-date coverage. Aggregate matched accepted claims back to all policy rows, preserving zero-claim rows. Reconcile incurred, recoveries, repudiations and quarantined pre-coverage claims. Avoid subtracting policy excess a second time where source amounts already reflect it.

Maintain distinct quantities: observed net incurred; estimated unreported losses; further development on reported claims; future recoveries; and any trend to 2025. State how these combine into each estimated-ultimate candidate.

For reporting completeness, use a peril-aware delay model that accounts for truncation at 31 December 2024, with pooling where claims are sparse. Check whether severity varies with reporting lag: count completeness is not automatically amount completeness. Prioritize bodily injury and subsidence, while reviewing other perils' open reserves.

Only one financial valuation exists. Historical paid/incurred development triangles cannot be reconstructed. Do not automatically increase open claims or select a 1.2–1.3 bodily-injury factor. Establish explicit low/base/high case-adequacy and future-recovery assumptions, including a case-adequacy factor of one as a reference. Any selected base needs a documented rationale.

A lower 2024 loss rate is diagnostic evidence, not proof of the amount of IBNR or reserve inadequacy. Avoid correcting the same effect through reporting, severity, inflation and final calibration. Retain an incurred-only diagnostic model while the maturity bridge is investigated.

**Acceptance evidence:** complete financial reconciliation, separate adjustment components, source and rationale for assumptions, and sensitivity of 2025 totals and model choice. Do not call adjusted losses observed ultimate.

## 5. Freeze validation before tuning

Use chronological folds: train 2021 and validate 2022; train 2021–2022 and validate 2023; then challenge on 2024 using training through 2023. Tune principally on earlier folds. Reserve 2024 for recency and development sensitivity rather than repeatedly fitting models, blend weights and calibration to it.

Recurring policies may remain across successive years, reflecting test construction. Add diagnostics for new policies/customers. Fit encoders, imputation and any estimated development parameters within the permitted training data. Freeze target scenarios before comparing models against them.

History predictors must respect both occurrence and reporting dates at each row's prediction date. Earlier-year financial histories cannot use December 2024 valuations as though those values were known earlier. Start with safe supplied predictors and reported-count history; defer historical amounts where their vintage is unavailable. Validate the timing of customer-level aggregates too.

Report fixed-power-1.5 pooled D², line-level deviance/D², observed- or scenario-loss/prediction ratios, prediction totals and runtime. Use sufficiently credible segments; accompany sparse-cell ratios with counts and uncertainty. Different-year D² values have different denominators, so compare candidates on the same rows and target version.

**Acceptance evidence:** split manifests, feature availability rules, no future claims in predictors, fixed target versions and paired model comparisons. All offline scores are incurred or adjusted proxies; they do not independently validate ultimate assumptions.

## 6. Build useful baselines and a valid file early

Use four references in order:

1. A global training-mean constant as a diagnostic. It need not score zero on a different holdout year.
2. Clean, line-specific loss cost per exposure multiplied by each row's exposure.
3. Written premium multiplied by a training-fitted line loss ratio, conditional on premium availability. It is a business comparator, not the technical target.
4. Three compact Tweedie GLMs with log links, exposure offsets, power 1.5 and a limited set of defensible factors.

Benchmark first against the observed reference, then repeat comparisons under the fixed maturity scenarios. Produce an early valid 626,639-row file; clearly identify its diagnostic target treatment. Do not wait for a complete reserving architecture to exercise the whole pipeline.

**Acceptance evidence:** predictions, scores, calibration, runtime and file checks available for each baseline on identical data and splits.

## 7. Add feature blocks and one model challenger

Motor candidates: driver age and validated licensing, NCB, cover, vehicle value/type/age, mileage, parking, excess and telematics opt-in/score. Home candidates: corrected log sum insured, building and occupancy characteristics, security, flood zone, river distance, elevation, soil and relevant weather interactions.

Evaluate reported-count history for returning risks and a separate written-premium challenger. Raw IDs are join/group keys. Exclude training-only renewal_decision and quarantine contact counts pending timing evidence. Test other customer aggregates for availability rather than assuming all supplied columns are prospective.

Supplied annual weather can support a conditional competition model. Compare it with a climatology variant built only from preceding training years in each fold. A model using realised 2025 annual weather is not automatically a quote-time tool; document that distinction.

Fit one LightGBM Tweedie model per line. Begin with power 1.5, modest trees, substantial minimum leaf sizes and regularisation. Start with a small search, for example 10–15 configurations per line after timing one representative fit. Expand only if gains justify the cost.

Exposure must be applied exactly once. GLM offsets must be present at training and prediction. For LightGBM, an initial score alone is incomplete unless validation, prediction and reload restore it correctly. An alternative rate-model formulation requires weights derived from the scoring contract: unweighted period-loss Tweedie deviance at p=1.5 corresponds to rate deviance weighted by sqrt(exposure), followed by multiplying predicted rate by exposure. Confirm weighting before choosing the implementation.

**Acceptance evidence:** block ablations; reliable offset/rate conversion; improved held-out deviance and acceptable calibration; stable results across folds and maturity sensitivities. Keep simpler models where evidence is inconclusive.

## 8. Earn additional complexity

Only add selected peril models where pooling, credibility and diagnostics support them. A bodily-injury or subsidence component may be more useful than an immediate system of thirty frequency/severity models.

Retain the largest claim in the primary reconciliation and report sensitivity. If fitting an attritional component with a cap, separately restore a justified large-loss allowance and test its stability. A flat load preserves a training total, not necessarily risk differentiation or future calibration.

Treat inflation, development and final calibration as distinct adjustments. Estimate trends from corrected exposures and changing risk mix, not raw rates. Apply a final calibrator or blend only using predictions not already optimized on those same outcomes; otherwise retain the uncalibrated candidate and disclose uncertainty.

**Acceptance evidence:** additional complexity improves fixed comparisons enough to justify runtime, fragility and explanation. Stop when gains disappear across folds/scenarios or when they are smaller than unresolved target uncertainty.

## 9. Record decisions and verify the submission

Each experiment records data/target/feature versions, code commit, split, parameters, seeds, predictions, D²/deviance, calibration, runtime and decision. Change one substantive assumption at a time. Reuse unchanged baseline results rather than needlessly refitting them.

Maintain a direction log: task → AI proposal → verification/human review → decision → measured impact. Record real errors and actual human decisions. AI self-checking is not evidence that a human approved the work. Useful candidates for review include exposure corruption, the customer-ID issue and unsupported development assumptions.

Create predictions by joining to sample row_id values. Reread the CSV and require exactly 626,639 rows; two columns row_id/prediction; unique IDs; complete exact test-ID coverage; finite numeric values; nonnegative predictions, with positivity for standard Tweedie scoring. Check exposure scaling and financial totals. Treat deviation from a forecast total as a review alert, rather than forcing agreement with an uncertain prior.

Save the file hash, configuration, model and submission record. The daily submission limit is five; unused daily slots do not accumulate. Submit purposeful candidates and explicitly select the final Part 1 entry.

**Acceptance evidence:** a pinned, controlled clean run reproduces the prediction file and its hash; meaningful invariant tests pass; submission metadata identifies the exact experiment.

## 10. Quality bar, scope and schedule

| Quality-bar requirement | Evidence to deliver |
| --- | --- |
| Actuarial judgement | Reconciliation, maturity/recovery assumptions, large-loss sensitivity and limits of identifiability |
| Pricing competence | Clean baselines, chronological comparisons, credible segment diagnostics and measured challenger gains |
| Effective AI use | Verified decisions and corrections with actual consequences |
| Trust and handoff | Reproducible scripts, data contracts, pinned environment and prediction provenance |
| Communication | Page-one findings and limitations; concise cards; running workflow demonstration |
| Part 2 adaptability | Reusable configuration, schema/profile comparison and an assumption register to revisit |

The current Kaggle header, verified 18 October, closes Part 1 on 23 October 2026 at 18:00 CEST / 16:00 UTC. The full event continues through Part 2. Working schedule, subject to actual availability and benchmarked runtime:

| Window | Required outcome |
| --- | --- |
| First working day | Clean layer, response reconciliation, frozen folds, baseline and checked prediction file |
| Next two working days | Maturity sensitivities, GLMs/LightGBM, selective feature comparisons |
| Penultimate day | Robustness, model choice, reproducibility and concise evidence |
| Final day | Buffer, rebuild, final checks and explicit submission selection |

If time is limited, remove additional models and tuning before weakening the data or validation controls. Preserve capacity for Part 2. The scope fits an actuarial/AI workflow demonstration; it does not claim established P&C pricing ownership or production deployment. Team size, daily hours and training runtime remain unverified.

Changes and conflicts to disclose:

- Use page one for findings, target and limitations, reconciling the quality bar with context.md's earlier Data-Card-first layout.
- Preserve GLM/GBM comparison but make ensembling conditional, revising the predetermined hybrid choice in context.md.
- Adjusted 2024 validation does not resolve the absence of ultimate labels. Earlier folds and sensitivity reporting qualify the quality bar's example holdout.
- Cards, SHAP and per-peril factors are chosen controls, not automatic proof of quality or verified professional-standard mandates. Check cited standards before claiming compliance.
- Parquet inputs and CSV submission are a conversion step, not a quality-bar conflict.

## Assumptions still requiring evidence

Exact score weighting/pooling; case reserve adequacy; amount-reporting completeness; future recovery patterns; sum-insured unit interpretation for exceptional records; timestamps of contact and customer aggregates; whether annual weather represents realised conditions, forecasts or scenarios; and practical team/time/compute capacity. None should be silently promoted to a confirmed fact.

## First three actions

1. Implement and review the deterministic data repairs and reconciliations.
2. Freeze validation and produce the first complete baseline prediction file.
3. Run a bounded maturity/recovery sensitivity study and a small GLM–LightGBM comparison before deciding on additional models.

## References

- Kaggle overview: https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/overview
- Kaggle data: https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/data
- Kaggle rules: https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/rules
- Standard Tweedie D² semantics and positivity: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.d2_tweedie_score.html
- LightGBM initial-score prediction handling: https://github.com/lightgbm-org/LightGBM/issues/5219
- Companion evidence: IAA_Part1_Audit_and_Revised_Approach.md and the audit.json produced from all eleven supplied Parquet files.
