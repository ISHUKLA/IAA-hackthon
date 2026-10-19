# Step 7 prompt algorithm — run the LightGBM challenger

Paste the prompt below into Codex or Claude Code from the repository root.

---

You are implementing and executing **Step 7: a bounded LightGBM Tweedie challenger** for the IAA AI-Assisted Actuarial Hackathon 2026 Part 1 repository.

## Objective

Test whether a nonlinear tree model produces a credible out-of-sample improvement over the selected Step 6 Tweedie GLM. Keep the data universe, response, exposure treatment, features, validation folds and scorer fixed so that the comparison isolates the effect of model family.

Complete the implementation, synthetic tests and real-data experiment when the prerequisites exist. Do not merely write a plan. Stop after Step 7. Do not blend models, add peril/frequency–severity architectures, execute Step 8, or create a final submission.

## 1. Read and verify the handoff

Read, in this order:

1. `context.md`
2. `what-good-looks-like.md`
3. `AGENTS.md`
4. the current status, assumptions, decisions and unresolved-issues documents
5. the Step 2 repaired-data manifest and feature exclusions
6. the Step 3 response and maturity documentation
7. the Step 4 fold, scoring and feature-availability contracts
8. the Step 5 baseline results and manifests
9. the Step 6 feature plan, ablations, accepted feature specification and manifests

Inspect the local working tree before acting. Local completed work may be ahead of the remote repository. Preserve unrelated edits. Update only the active-scope section of `AGENTS.md` to authorise Step 7 modelling while retaining every existing safety, data and publication control. Create `prompts/step7/00-lightgbm-challenger.md` containing this execution contract.

Verify that the selected Step 6 GLM can be reproduced and that Step 4–6 share:

- the same repaired policy and claim universe;
- the same response/scenario version;
- the same clean exposure definition;
- the same F2023 primary and F2024 challenge fold memberships;
- the same period-cost Tweedie D² scorer at power 1.5;
- the same eligible feature set and timing rules.

Do not compare scores across incompatible targets, folds or claim universes. If Step 6 is missing, failed, or irreproducible, implement independent Step 7 code and synthetic tests where useful, but mark the real experiment `blocked` with the exact prerequisite. Do not silently invent a GLM benchmark or random split.

## 2. Freeze the comparison before fitting

Create `configs/step7_lightgbm.json` before training. Record:

- the Step 6 benchmark model ID and prediction hashes;
- data, claim-universe, response, scenario and fold IDs;
- one explicit feature allowlist per insurance line;
- prohibited features and timing conditions;
- the exposure/rate formulation;
- the bounded hyperparameter candidates;
- seeds, early-stopping rule and resource limits;
- selection criteria and the one-time F2024 challenge rule;
- software versions and output paths.

Phase A must use exactly the selected Step 6 features. Do not add features while changing model family. If Step 6 identified a feature block as eligible specifically for nonlinear testing, it may be evaluated only in a separately labelled Phase B after Phase A, one block at a time and on F2023 only. Never merge that result into the model-family comparison.

Exclude raw identifiers, same-period claims and outcomes, final claim status, target/scenario columns, response provenance, `renewal_decision`, customer-service contacts, timing-unsafe history, and any feature rejected by the Step 4/6 availability registry. `row_id`, policy, customer and address identifiers may be used for controlled joins, grouping and alignment only—not as predictors.

## 3. Implement a consistent Tweedie objective

Train one LightGBM model for each of motor, buildings and contents using:

- Tweedie objective;
- `tweedie_variance_power = 1.5`;
- positive finite clean exposure;
- annual loss rate as the training response;
- the exposure weights required by the current provisional unweighted period-cost objective;
- policy-period cost as the final prediction.

For each row with period response `Y` and clean exposure `e`:

```text
y_rate = Y / e
sample_weight = e ** 0.5
period_prediction = predicted_rate * e
```

This follows the identity `d_p(Y, e*r) = e^(2-p) d_p(Y/e, r)` at `p = 1.5`. Score `period_prediction` with the unchanged Step 4 scorer. Training weights are not metric weights. Do not score annual rates and do not multiply exposure twice.

If the repository already contains a verified offset implementation that is exactly consistent during training, validation, prediction and model reload, it may be reused instead. Do not use LightGBM `init_score` as a casual substitute for an offset: prediction and reload behaviour must be explicitly tested. Record the chosen formulation and reject mixed formulations within a comparison.

Require non-negative training responses. Investigate rather than clip any negative response. LightGBM predictions must be finite and strictly positive before conversion to period cost. Any numerical floor must be declared in the configuration and used only for metric-domain safety, not calibration.

## 4. Build a leakage-safe feature pipeline

Reuse the Step 6 feature builders and joins. LightGBM may use missing numeric values directly, but missingness semantics must remain explicit:

- distinguish ordinary missing data from structural telematics non-participation;
- keep opt-in status separate from telematics score;
- preserve adopted repair flags and original values where the data contract requires them;
- create categorical vocabularies from the fold’s training rows only;
- map unseen held-out categories deterministically without learning from the held-out target;
- calculate history features using information reported strictly before the policy-period prediction date;
- prevent duplicate-producing joins and verify one row per `row_id` after every join;
- keep whole-year contemporaneous weather and other conditional features out of the core challenger unless already accepted under the same Step 6 availability interpretation.

The prepared training table contains outcome fields. Apply the explicit allowlist immediately before constructing the model matrix and save the actual feature names used by every fitted model.

## 5. Use a bounded model search

Start by timing one conservative configuration on a representative line and fold. Based on actual runtime and memory, predeclare a small candidate list—normally no more than 8 configurations per line and never more than 15 without stopping and documenting why expansion is justified.

Vary only a compact set of consequential controls:

- `num_leaves` or a corresponding `max_depth` constraint;
- `min_child_samples` / minimum leaf size;
- learning rate and maximum boosting rounds;
- L1/L2 regularisation;
- optional feature and row subsampling.

Use large enough leaves for portfolio credibility and control overfitting. Use early stopping on the F2023 validation data, with a generous declared round cap. Fix every random seed. Do not run a broad Cartesian grid, Bayesian optimisation, repeated leaderboard search, GPU migration, neural network, or automatic feature discovery.

For every line, include one conservative reference configuration. If additional configurations do not produce a material F2023 improvement, stop the search rather than consuming the full budget automatically.

## 6. Select on F2023 only

For each line and configuration:

- train on the F2023 training years only;
- predict the complete F2023 validation membership;
- save row-level period-cost predictions with immutable model/config/input identifiers;
- evaluate using exactly the Step 4 power-1.5 period-cost scorer;
- compare against the Step 6 GLM on identical IDs and the identical response version.

Report:

- pooled and line-level Tweedie D²;
- mean and total Tweedie deviance;
- observed/scenario and predicted totals;
- actual-to-expected ratios and calibration by prediction band;
- new versus returning risks and material risk segments;
- high-cost and high-prediction tail behaviour;
- sensitivity with the largest bodily-injury claim retained and separately described;
- training rounds, runtime, peak memory where measurable, convergence and model size.

Use paired row-level deviance differences. Do not average the three line-level D² values and call that the pooled competition score. Do not select a configuration from training fit, feature importance, SHAP values or the number of wins across hand-picked segments.

Select one fixed LightGBM specification per line on F2023. Record all attempted configurations, including failures. Freeze the chosen configurations, boosting rounds or refitting rule, features, seeds and preprocessing before accessing F2024.

## 7. Confirm once on the F2024 challenge fold

Refit the frozen per-line configurations using the approved F2024 training years and evaluate once on the complete 2024 challenge membership. Do not retune after seeing the result. If F2024 was already used during Steps 5–6, call it a reused development challenge—not an untouched holdout.

Compare the frozen LightGBM challenger and frozen Step 6 GLM on the same F2024 rows. Report whether the direction and approximate size of the F2023 improvement persist. Investigate material calibration drift, line reversals and tail concentration. Do not alter the target-development scenario because one model looks better under another constructed response.

Step 7 may conclude:

- `lightgbm_preferred_for_step8`;
- `glm_preferred_for_step8`;
- `inconclusive`;
- `blocked`.

LightGBM should be preferred only when its out-of-sample gain is meaningful relative to score variability, is not driven solely by a few extreme claims, does not introduce material calibration or leakage concerns, and is proportionate to its extra runtime and explanation burden. A numerically higher single-fold score is insufficient.

Step 8—not this step—will decide whether additional complexity such as a blend, peril decomposition or frequency–severity structure is earned.

## 8. Explain the model without overstating interpretation

For the selected LightGBM candidates, save:

- split and gain feature importance;
- prediction and residual summaries;
- calibration plots/tables;
- a small, fixed out-of-sample SHAP sample if the installed environment supports it safely;
- selected partial-dependence or accumulated-local-effect diagnostics for the most material auditable features.

Use only out-of-sample or target-independent explanations where possible. Verify that displayed effects make actuarial and data-quality sense. State clearly that importance and SHAP describe model behaviour; they do not prove causality, data availability or predictive improvement.

Do not add SHAP as a blocking dependency if it would destabilise the tested environment. In that case, record it as unavailable and retain the other diagnostics.

## 9. Test the implementation

Add repository-consistent commands such as:

- `make step7-check`
- `make run-lightgbm-challenger`
- `make step7-acceptance`

Synthetic tests must cover:

- the period/rate Tweedie deviance identity;
- exposure applied exactly once;
- deterministic training with fixed seeds;
- train-only category handling and unseen categories;
- structural and ordinary missingness;
- strict history/report-date cut-offs;
- rejection of outcome and ID features;
- exact row-ID alignment and no join multiplication;
- positive finite predictions;
- saved-model reload prediction equivalence;
- held-out-target perturbation not changing fitted features or model parameters;
- failure on incompatible fold, response or upstream hashes.

Real-data acceptance must additionally verify:

- all three lines trained or have an explicit failure status;
- complete held-out prediction coverage;
- identical scored rows for GLM and LightGBM;
- consistent metric, response and exposure units;
- unchanged upstream inputs;
- actual runtime and environment captured;
- F2024 was accessed only after the selected configuration was frozen.

Synthetic success is not real-data completion. Missing data or an unavailable LightGBM dependency must produce an honest `blocked` or `partial` status, not a passing acceptance report. Add and pin only the minimum compatible dependency required; run the project’s dependency and regression checks after installation.

## 10. Save evidence and hand off to Step 8

Store large or generated artifacts under ignored `outputs/step7/`, including:

- fitted models and preprocessing objects;
- row-level predictions;
- metrics and paired-deviance results;
- search history and early-stopping records;
- feature lists and explanation artifacts;
- an immutable run manifest containing input/config/code-content hashes, Git state, environment, seeds and measured runtime.

Create or update:

- `configs/step7_lightgbm.json`
- `docs/step7/lightgbm-results.md`
- `docs/step7/acceptance.md`
- `outputs/step7/decision.json`
- `MODEL_CARD.md`
- feature registry, assumptions, decision log, status and `PROMPT_LOGS.md`

The results report must contain a direct GLM-versus-LightGBM table for F2023 and F2024, overall and by line, together with calibration, tail behaviour, runtime and limitations. Distinguish actual measurements from interpretations and unresolved assumptions.

Finish with:

1. prerequisites and exact versions used;
2. features and exposure formulation;
3. bounded configurations tried;
4. tests and commands actually run;
5. exact F2023 and F2024 GLM-versus-LightGBM results;
6. calibration, tail, runtime and stability findings;
7. the Step 7 decision and its evidence;
8. unresolved target and feature-timing uncertainty;
9. the exact command that reproduces the run.

## 11. Hard boundaries

- Stop after Step 7; do not execute Step 8 or Step 9.
- Do not blend GLM and LightGBM predictions.
- Do not add peril, frequency–severity, neural-network or stacking architectures.
- Do not tune on F2024, the 2025 test predictions or Kaggle feedback.
- Do not create or upload a final Kaggle submission.
- Do not contact organisers.
- Do not commit, push, merge, tag or publish unless explicitly requested.
- Do not invent ultimate labels, historical financial snapshots, actuarial approval, leaderboard scores or successful real-data execution.
- Do not ask for routine approval between substeps. Continue automatically unless blocked by missing authority, missing data, incompatible evidence or a material methodological choice that the repository cannot resolve.

---

## Intended interpretation

Step 7 answers:

> Does a controlled nonlinear Tweedie model produce a repeatable and credible improvement over the transparent Step 6 GLM on exactly the same prediction problem?

Keeping the GLM is a successful outcome when the evidence for LightGBM is weak, unstable or not worth the additional complexity.
