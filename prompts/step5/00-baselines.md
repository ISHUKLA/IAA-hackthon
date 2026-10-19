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
