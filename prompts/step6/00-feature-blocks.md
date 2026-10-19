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
