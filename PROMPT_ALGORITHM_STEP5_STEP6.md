# IAA Part 1 — Prompts for S5 and S6

Prepared 19 October 2026 for https://github.com/ISHUKLA/IAA-hackthon . These are implementation instructions for a local Codex or Claude Code harness. No models or feature experiments were run to prepare this file.

**S5 builds simple baselines. S6 tests feature improvements using the same model family and frozen comparison.** The LightGBM challenger remains S7. This follows the agreed implementation numbering; headings in the older planning document may use different section numbers.

Run S5 first, review its evidence, then run S6. Each prompt authorizes its complete reversible implementation; there is no need to ask for confirmation after every routine substep. Missing human actuarial decisions remain visibly pending.

## S5 — Implement and evaluate reference models

Copy the complete block below into the harness while the repository is open. If this guide is attached, you can instead request execution of this S5 section.

```text
Implement S5 of the IAA Part 1 project: reproducible, informative baseline models
using the completed Step 4 validation framework. Complete the bounded work below
and stop before S6. Do not merely propose how to implement it.

1. READ AND CHECK THE CURRENT STATE
Read context.md first, then what-good-looks-like.md, AGENTS.md, the current
source register/status, Steps 2–3 handoffs, and the local Step 4 validation plan,
configuration, feature registry and acceptance report. Preserve the briefs.
Update only AGENTS.md's active scope to permit S5 modelling and the local
pipeline-check prediction file; preserve its other controls. This prompt supplies
that authorization and does not authorize publishing, committing or uploading.

Inspect local code/manifests rather than assuming the latest work was pushed.
Run the existing synthetic gates and actual Step 4 acceptance if inputs exist.
Confirm policy, deduplicated/original claim universe, responses, scenarios and
reporting fits share the chosen upstream versions. The later repair candidate
has 162,546 claims and a provisional net observed total of 741,156,868.43 CU;
the old raw population has 163,150 and 744,330,677.04 CU. These are conditional
references to verify, not constants to force or permission to mix universes.

If Step 4 is missing or inconsistent, implement independent baseline code and
synthetic tests, but mark real training/evaluation blocked with its exact missing
prerequisite. Do not invent folds or silently substitute random validation.

2. FREEZE THE BASELINE EXPERIMENT
Write configs/baselines.json with model IDs, allowed core fields, preprocessing,
response versions, training population, fold IDs, scoring settings and a small
resource budget. Use the local Step 4 contract: normally F2023 is the main
comparison (train 2021–2022, validate 2023), with F2024 the recent-year challenge
(train 2021–2023, validate 2024). F2022 is an optional robustness check.

Keep retrospective_snapshot_proxy labels: December 2024 financial values were
not known at earlier simulated prediction dates. Observed incurred and supported
case scenarios are not true ultimate outcomes. Keep unavailable monetary IBNR,
future recoveries, financial basis and adoption decisions explicit. Do not add
an arbitrary development or inflation factor to make a baseline look plausible.

3. BUILD BASELINES IN THIS ORDER, FITTING ONLY ON THE FOLD'S TRAINING ROWS
B0: predict the global training mean of policy-period response on every held-out
row. Do not use the validation mean as a predictor. This constant need not have
D² zero; the metric's internal null uses the scored response mean.

B1: for each line calculate sum(training response)/sum(clean training exposure)
and predict that annual rate times the held-out row's clean exposure.

B2: a conditional business comparator, written premium times a training-fitted
line loss ratio. First establish premium units, period/annual basis and availability.
If unsupported, report B2 unavailable and continue. Handle invalid/zero premiums
through a predeclared training-only fallback to B1 or an unavailable-model status;
do not drop validation rows and present its score as directly comparable.

B3: one compact Tweedie GLM per line, power 1.5 and log link, with a small set
of audited, prospectively interpretable core factors. Examples to map to actual
columns: motor age, cover and vehicle/mileage; home sum insured, construction,
occupancy and a credible geographic/flood factor. Keep premium and uncertain
weather/history/customer snapshots out of B3's core specification.

Use sparse category encoding with train-fitted unknown/rare handling and numeric
imputation/scaling fitted only on training. Preserve structural missingness and
repair/adoption flags. Do not include IDs, same-period claim counts/costs,
renewal_decision, customer_service_contacts or outcome/provenance fields in X.

4. IMPLEMENT EXPOSURE CORRECTLY
Do not treat exposure as an unconstrained replacement for an offset. Use a
verified implementation of log(exposure) offset and its appropriate variance/
weight convention, or the following equivalent rate-loss formulation for the
current provisional unweighted period-cost objective:

  y_rate = period_response / exposure_clean
  fit TweedieRegressor(power=1.5, link='log') with
      sample_weight = exposure_clean ** 0.5
  period_prediction = predicted_annual_rate * exposure_clean

The equivalence concerns deviance; document normalization/regularization rather
than claiming arbitrary penalty settings are identical across implementations.
Those weights are training weights. Score the period predictions through Step 4
with its unchanged metric weights; do not score rates or call the estimator's
rate-space score the competition result. Validate positive finite exposure.

Start with one modest regularization setting. If needed, predeclare at most
three strengths per line on F2023; record convergence, runtime and matrix size.
Avoid dense high-cardinality one-hot matrices and quadratic-memory solvers.
Only the chosen fixed specification proceeds to F2024; do not repeatedly tune
against its results or keep calling it untouched after it informs changes.

5. EVALUATE FAIRLY AND PRESERVE THE EVIDENCE
Use the existing power-1.5 scorer on identical held-out IDs and response versions.
Report pooled/line D², mean/total deviance, reference and predicted totals,
reference A/E, returning/new and material segment diagnostics, convergence and
runtime. Keep the large BI claim in primary results; tail sensitivity is separate.
Report undefined D² and failed fits honestly. Do not silently clip predictions.

Compare B3 against B0/B1 and eligible B2. Use paired deviance on common rows;
do not average line D² into a pooled score. Evaluate supported fixed response
scenarios as sensitivity, comparing models within each response version. A better
score against another constructed target does not prove better ultimate accuracy.
Keep unchanged baseline results when inputs/configuration/code are unchanged.

6. TEST AND MAKE THE WORK REPRODUCIBLE
Implement make step5-check, make run-baselines and make step5-acceptance,
or equivalent commands consistent with this repository. Synthetic tests must
cover known baseline arithmetic, train-only fitting, leakage rejection, unseen
categories, exposure scaling, prediction save/reload and exact row alignment.
Use a synthetic example to check the period/rate deviance identity. Real-data
acceptance must verify actual inputs, complete held-out coverage, positive finite
predictions, unchanged upstream hashes, convergence status and consistent units.
Preserve prior checks; distinguish unavailable inputs from passing acceptance.

Store fitted objects, row predictions and manifests only under ignored
outputs/step5/. Record source/config/code-content hashes including uncommitted
edits, environment, feature/target/fold IDs, seeds and measured runtime. Add only
necessary dependencies and lock the environment actually tested.

7. EXERCISE THE FILE PIPELINE WITHOUT CLAIMING A FINAL SOLUTION
After the real-data gates pass, fit B1 on all permitted 2021–2024 training rows
and generate a local baseline_pipeline_check.csv for the supplied 2025 rows.
Use the current submission checker and sample IDs: exactly row_id,prediction,
no index, unique exact coverage, finite nonnegative amounts and sample order as
a project convention. The known reference count is 626,639; verify it locally.
Keep the CSV ignored and attach metadata identifying its provisional response,
unresolved ultimate/IBNR assumptions and pipeline-check purpose. No fabricated
2025 labels, leaderboard score, claim of final readiness or upload is permitted.

8. DOCUMENT AND FINISH
Write docs/step5/baseline-results.md and acceptance.md with actual outcomes,
supported comparisons, failures/limitations and exact rerun commands. Update
MODEL_CARD.md, assumptions, status and PROMPT_LOGS.md proportionately. Record
real AI proposals, verification and human decisions; do not invent oversight.

Acceptance: real baseline outputs can be rebuilt and compared on the frozen
protocol; no baseline is described as validated ultimate truth. No improvement
is a legitimate result to explain. Report changes, tests, scores, runtime,
remaining decisions and the S6 handoff. Do not execute S6 or train LightGBM.
Do not spawn agents, commit, push, publish, contact anyone or upload a submission.
```

## S6 — Implement and test feature blocks

Copy this complete block after S5 has produced its handoff. If the guide is attached, request execution of this S6 section only.

```text
Implement S6 of the IAA Part 1 project: audited feature engineering with measured
incremental value over the S5 GLM. Complete this step and stop before S7.

1. CHECK THE HANDOFF AND FREEZE WHAT WILL BE COMPARED
Read context.md, then what-good-looks-like.md, AGENTS.md, the latest data/source
register and Steps 2–5 acceptance, configurations and actual manifests. Inspect
git status and preserve unrelated work. Update only AGENTS.md's active scope
to permit S6 feature implementation and its bounded model refits.

Verify the baseline run is complete and uses consistent input/claim/response
versions. Reuse the actual local Step 4 folds, metric, scenario protocol and
feature timing registry. Keep S5's model family, regularization and other fit
settings fixed for the initial ablations: a simultaneous model/target change
would prevent attribution of any improvement to the new features.

If a prerequisite is missing, implement independent feature code/tests and state
exactly which real experiment is blocked. Do not invent a baseline score, silently
rebuild a different validation design or infer completion from published status.

2. INVENTORY THE REAL COLUMNS AND WRITE A SMALL FEATURE PLAN
Create configs/features.json and docs/step6/feature-plan.md from the actual
schema and S5 diagnostics. For each proposed feature record source columns,
units, transformation, timing/availability, hypothesis, target segment, missing/
unknown behavior and adoption status. Map the following ideas to actual columns;
mark missing or unsupported fields unavailable rather than inventing them.

Choose at most three primary feature blocks per line for the first pass. Rank
them by measured residual/segment problems, data quality and implementation cost.
Do not generate a generic catalogue of hundreds of interactions.

3. IMPLEMENT THE HIGHEST-PRIORITY ELIGIBLE BLOCKS
Motor: test simple nonlinear age/licensing effects, mileage/vehicle/cover
relationships and ordinary missingness flags. Preserve questionable NCB, zero
mileage or engine-capacity values unless their correction is supported. A
plausibility flag is not an organiser-confirmed error.

Home: test declared log/binned sum insured using the adopted raw or repaired
candidate basis, construction/occupancy/security and credible hazard features
such as flood zone, river distance, elevation or soil where actually supplied.
Inspect sums/units before ratios or logs. Derive from the approved candidate
once; never divide an already repaired value by 1,000 again. Preserve competing
bases as separately labelled sensitivity if adoption is pending.

Telematics: preserve opt-in and structural missingness. Only admit score-based
features when the measurement window supports the experiment's prediction date;
otherwise keep a conditional branch or exclude. A blank score must not be
interpreted as a genuinely poor measured score of zero.

History, only where reconstructible: prior reported counts/recency and prior
observed coverage on the relevant policy/customer. Respect both loss attribution
and report visibility strictly before the row's period_start, using Step 4's
date-boundary convention and canonical keys. Distinguish observed zero history
from no supplied history. Do not use the final 2024 claim status or current
paid/incurred amounts as historical predictors. Use the chosen claim universe
consistently; do not reintroduce removed copies through a second history join.

Weather: prior-year climatology may be tested using only years available before
the row's prediction date, with explicit handling of new addresses/short history.
Whole-year contemporaneous weather remains a separate conditional experiment;
it must not enter the core quote-time model through a generic weather join.

Existing tariff: written premium/discount may be a separately named challenger
block after their units and prospective availability are established. Preserve a
tariff-independent core result so borrowed tariff information is visible.

4. ENFORCE TRAIN-ONLY FITTING AND SAFE JOINS
Fit imputation, scaling, bin/spline cutpoints, rare-category pooling and any
learned aggregates on training only. Use guarded joins preserving unique row_id
and exact row counts/order. Keep exposure out of these free feature effects
unless explicitly justified; its established cost conversion remains unchanged.

Exclude raw IDs, renewal_decision, customer_service_contacts, same-period claim
counts/costs, targets/scenarios and target provenance. Reapply the explicit
allowlist after every join; a prepared model table can contain response columns.
Target encoding remains disabled in this bounded pass. Do not fit transforms on
2025, use validation outcomes to define bins or generate synthetic target labels.

5. RUN PAIRED ABLATIONS WITH A BOUNDED BUDGET
On F2023, evaluate the frozen S5 GLM alone, then the same GLM plus one block
at a time. Save complete same-row predictions, runtime and block identity.
Use paired period-loss deviance and the Step 4 diagnostics; inspect calibration,
line/returning/new segments, sparse groups and the retained extreme BI claim.

Retain useful blocks and test one combined candidate per line. Freeze that
candidate before evaluating F2024. Reuse existing baseline predictions when
their provenance matches. F2022 is optional if gains look unstable and resources
permit. If F2024 already informed earlier decisions, label it a development
challenge rather than an untouched independent check.

Repeat the supported response-scenario sensitivity with comparable baseline/
candidate pairs within each version. Do not select a response or accounting
basis because it flatters a feature. Gains against proxies are not proof of
ultimate accuracy. Record weak, unstable or absent gains as such; retaining the
S5 specification is an acceptable outcome. No broad parameter search, boosting,
ensemble, new reserving model or full feature-by-scenario combinatorial sweep.
Lack of GLM improvement does not prove an eligible feature is useless for a later
nonlinear model. It may remain a labelled S7 candidate, not a demonstrated gain.

6. VERIFY MECHANISMS AND SAVE RESULTS
Implement make step6-check, make run-feature-experiments and make
step6-acceptance, or equivalent repository commands. Synthetic tests should
exercise unchanged row identity, future-report exclusion, no future-year weather,
training-only fitted statistics, unseen categories, structural missingness,
original/candidate insured units, and feature/prediction save-reload consistency.
With the experiment configuration fixed, changing held-out outcomes must not
change training-fitted features or model parameters. Legitimately available
held-out predictors may change predictions.

Real-data checks must verify dimensions, feature allowlists, cutoff provenance,
upstream immutability, finite valid predictions and consistent metric/exposure
units. Keep existing gates passing and real-data acceptance separate from
synthetic tests. Failure/unavailable status must not be recorded as success.

Store row-level features/predictions/fitted objects under ignored outputs/step6/.
Version small configurations, code, schemas and aggregate reports. Record actual
code/input/config hashes including uncommitted changes, seeds, environment,
feature/fold/target IDs, fit settings and measured runtime. Do not overwrite the
baseline or claim feature usefulness from in-sample fit or importance alone.

7. DOCUMENT THE DECISION AND STOP
Write docs/step6/feature-results.md with a table: block, hypothesis, availability,
main-fold deviance/D² change, calibration/segment effect, challenge result where
run, runtime and retain/reject/conditional decision. Include the tested combined
specification and the uncertainty attached to target and feature timing.

Update MODEL_CARD.md, feature registry, status, assumptions and PROMPT_LOGS.md.
Record genuine verification and human decisions only. Flag any conflict between
the briefs and available evidence; do not invent an ultimate target, mandatory
method, actuarial signoff, efficiency gain or successful experiment.

Acceptance: each retained feature block has a prospective rationale and useful
held-out evidence, or is explicitly a conditional candidate for later testing.
Deliver the selected core feature specification, reproducible transforms,
predictions, experiment comparisons and unresolved items to S7. S7 will test
LightGBM on the same protocol. Report results and stop; do not execute S7,
spawn agents, commit, push, publish, contact anyone or upload a submission.
```

## Technical note — exposure and the GLM objective

The rate-model weighting above is a derivation from the chosen scoring objective, not a claim that every actuarial GLM uses those weights. For period loss `Y`, positive exposure `e`, annual prediction `r` and Tweedie unit deviance `d_p`:

`d_p(Y, e*r) = e^(2-p) * d_p(Y/e, r)`.

Consequently, at `p=1.5`, minimizing unweighted period-cost deviance corresponds to rate deviance weighted by `sqrt(e)`. A training implementation normalizing by total sample weight changes the overall loss scale, which matters when comparing regularization penalties across formulations. Using exposure as the rate-training weight is another objective; it should not be copied from an example while claiming exact equivalence to the provisional unweighted period-cost score.

The scaling identity was checked arithmetically for zero/positive responses, short/full/leap-year exposure and differing annual rates when preparing this guide. This is a check of the stated identity, not a test of a trained model or the future implementation.

## Sources and current-state caveats

- The project sources inspected were the current repository briefs, `AGENTS.md`, plan/status and Step 2 repair record. The repository still exposes Step 3 as its active scope; Steps 4–6 may exist only in your local checkout. Each prompt checks local completion before execution and updates only its active scope.
- The baseline/feature boundary follows the consolidated approach and the Step 4 guide. Current code/configuration and manifests must be checked before execution; old counts are not promoted to new audit measurements.
- Official estimator reference: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.TweedieRegressor.html . Verify arguments against the pinned installed version.
- Official insurance example: https://scikit-learn.org/stable/auto_examples/linear_model/plot_tweedie_regression_insurance_claims.html . Its exposure-weighted rate example has its own scoring convention; the local contract determines the formulation used here.

No new competition-rule interpretation is asserted. Official pooling/weights and the financial target interpretation retain their existing unresolved status.
