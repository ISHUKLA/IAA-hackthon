# Step 8 prompt algorithm — make additional complexity conditional

Paste the prompt below into Codex or Claude Code from the repository root.

---

You are implementing **Step 8: make additional modelling complexity conditional** for the IAA AI-Assisted Actuarial Hackathon 2026 Part 1 repository.

## Objective

Do not add complexity merely because it is available. Start from the best credible model produced by Steps 5–7 and introduce **at most one justified complexity at a time**. Every candidate must respond to a documented weakness, use the frozen validation protocol, and clear a predeclared promotion gate. A valid Step 8 outcome is **“retain the current benchmark.”**

This step is an evidence-controlled model-selection exercise. It is not permission to build every possible model, optimise against the 2024 challenge fold repeatedly, or create a final Kaggle submission.

## 1. Preflight and scope

Read, in this order:

1. `context.md`
2. `what-good-looks-like.md`
3. `AGENTS.md`
4. the current status, assumptions, decisions and unresolved-issues documents
5. the Step 2–4 data, response and validation contracts
6. all Step 5–7 experiment manifests, model cards, scores, calibration reports and diagnostics
7. the competition metric and submission contract already recorded in the repository

Then:

- inspect the working tree and preserve unrelated user changes;
- verify the input hashes and that Steps 5–7 used the same repaired claim universe, response version and fold definitions;
- record whether the current leader is the Step 6 GLM or Step 7 nonlinear challenger;
- freeze its model settings, feature list, response construction, folds and scoring code as the **Step 8 benchmark**;
- update only the active-scope section of `AGENTS.md` to Step 8 while retaining all existing controls;
- create `prompts/step8/00-conditional-complexity.md` containing this execution contract.

Stop with a precise blocker if the Step 5–7 evidence is missing, irreproducible, uses incompatible response versions, or does not identify a credible benchmark. Do not silently repair model results or compare scores from different universes.

## 2. Diagnose before proposing complexity

Create `reports/step8/benchmark-diagnosis.md`. Use out-of-sample results—not training fit—to identify the benchmark’s most material weakness. Examine:

- pooled and line-level Tweedie D² and mean Tweedie deviance;
- observed versus predicted totals and loss cost per exposure;
- calibration by prediction decile, insurance line and exposure band;
- performance in large-loss and high-prediction tails;
- residual patterns for the main validated risk dimensions;
- stability between the 2023 primary fold and the 2024 challenge fold;
- runtime, memory, reproducibility and interpretability;
- whether any apparent weakness is caused by response immaturity, claim duplication, missingness, unit errors or leakage rather than model form.

Clearly distinguish facts, interpretations and unresolved uncertainty. Select **one primary weakness**. If no material, reproducible weakness is demonstrated, record `decision: retain_benchmark`, skip modelling, complete the reporting in section 7, and stop Step 8 successfully.

## 3. Select one hypothesis-led candidate

Create `configs/step8_complexity_gate.json` before fitting anything. It must record the benchmark, diagnosed weakness, proposed candidate, causal rationale, additional parameters/features, computational budget, prohibited information, evaluation measures and promotion thresholds.

Choose only the smallest candidate capable of testing the diagnosis. Permitted candidate families, when justified, include:

- **frequency–severity or hurdle structure** when residual evidence shows that claim occurrence and positive cost require different relationships;
- **peril decomposition** when peril mix is materially heterogeneous and peril labels can be constructed consistently without post-period information; component predictions must reconcile exactly to the policy-period total;
- **one-dimensional GLM–LightGBM blend** when the two frozen models make meaningfully different, complementary errors;
- **restricted interactions or monotonic/nonlinear transformations** when specific residual structure remains;
- **line-specific refinement** when the weakness is isolated to one insurance line;
- **fold-safe maturity adjustment sensitivity** only when the claim-development method, valuation cut-offs and uncertainty were already established and can be recreated without using held-out outcomes.

Do not automatically add peril models, claim development, external data, neural networks, stacking, broad hyperparameter searches or ensembles of many models. Do not introduce several candidate families together. Do not treat feature importance or SHAP values as proof that added complexity improves prediction.

If the proposed candidate relies on unresolved timing, annual weather availability, telematics measurement windows, premium basis, historical financial snapshots or unverified ultimate labels, mark it ineligible and retain the benchmark unless a leakage-safe version can be demonstrated from existing evidence.

## 4. Predeclare a promotion gate

Before training, define materiality from score uncertainty and operational cost. Estimate score variability with an appropriate method such as policy/customer-cluster bootstrap on fixed out-of-sample predictions; repeated random seeds may measure algorithmic instability but must not be presented as independent temporal validation.

The candidate may be promoted only if all applicable gates pass:

1. it improves the **2023 primary-fold** pooled competition metric by more than numerical noise and the predeclared materiality threshold;
2. the gain is not solely caused by a handful of extreme observations or one unexplained segment;
3. calibration is not materially degraded overall or in a major insurance line;
4. prediction totals and tail behaviour remain plausible and all predictions satisfy the metric domain;
5. it passes leakage, feature-timing, ID-alignment, exposure and reproducibility checks;
6. its incremental complexity is proportionate to the measured benefit;
7. after selection is frozen, the **single 2024 challenge-fold confirmation** shows directionally consistent evidence within the declared uncertainty tolerance.

Do not invent a universal D² threshold. Derive and record a threshold from the observed uncertainty, benchmark performance and practical cost. Do not tune the threshold after seeing candidate results. If 2024 has already been consulted repeatedly during Steps 6–7, label it honestly as a reused challenge set and do not call it untouched confirmation.

## 5. Implement and test the minimum experiment

- Reuse the exact Step 7 preprocessing, scorer and fold runner wherever possible.
- Change only the components required by the registered hypothesis.
- Fit and select on the 2023 primary fold.
- Keep the 2024 challenge fold inaccessible until the candidate and decision rule are frozen.
- Use train-only fitting for imputers, encoders, feature selection, reporting-delay models and blend weights.
- For a blend, optimise only one weight on the primary fold, constrain it to `[0,1]`, include both endpoints, and compare it against both component models.
- For peril or frequency–severity models, prove row-level reconciliation to total policy-period predictions and apply exposure exactly once.
- Retain raw values and repaired inputs unchanged.

Add focused automated tests for:

- deterministic reruns and saved-model reload equivalence;
- exact row-ID alignment and absence of duplicates;
- finite, non-negative predictions, and strictly positive predictions where the scorer requires them;
- no use of held-out targets, current claim outcomes, final status or post-period information;
- train-only preprocessing and feature creation;
- policy/customer group separation where relevant;
- exposure arithmetic and no double multiplication;
- reconciliation of decomposed predictions;
- no material score change when held-out outcomes are perturbed before prediction;
- rejection of incompatible response versions or input hashes.

Run both synthetic edge-case tests and the actual-data experiment. Synthetic success must never be reported as real-data performance.

## 6. Make the decision

Write `outputs/step8/decision.json` with one of:

- `promote_candidate`
- `retain_benchmark`
- `inconclusive`
- `blocked`

Include benchmark and candidate identifiers, hashes, exact features, folds, scores, uncertainty estimates, calibration and tail checks, runtime, gate results and reasons. A small score gain that fails stability, leakage, calibration, reproducibility or proportionality checks must not be promoted.

Never choose a candidate merely because its single observed score is numerically highest.

## 7. Required outputs and handoff

Create or update:

- `configs/step8_complexity_gate.json`
- `prompts/step8/00-conditional-complexity.md`
- `reports/step8/benchmark-diagnosis.md`
- `reports/step8/candidate-comparison.md`
- `reports/step8/acceptance.md`
- `outputs/step8/decision.json`
- the experiment log, model card, assumptions register, decision log and current-status document
- reproducible commands or Make targets for the Step 8 checks and experiment

The comparison report must show, for benchmark and candidate, primary and challenge results, line-level results, calibration, tail diagnostics, uncertainty, runtime and added complexity. State which results are factual measurements and which conclusions are judgement.

Finish with:

1. the benchmark and diagnosed weakness;
2. the candidate tested and why it was the minimum adequate test;
3. actual commands and tests run;
4. exact primary and challenge results;
5. every promotion gate as pass/fail/not testable;
6. the decision and remaining uncertainties;
7. the command that reproduces the result.

## 8. Hard boundaries

- Stop after Step 8. Do not execute Step 9.
- Do not create or upload the final Kaggle submission.
- Do not contact organisers.
- Do not commit, push, merge or publish unless explicitly requested.
- Do not replace provisional observed costs with invented ultimate labels.
- Do not claim actuarial sign-off, official metric equivalence or production readiness.
- Do not use the test-set target, submission feedback or repeated challenge-fold inspection for tuning.
- Do not ask for routine approval between substeps. Continue automatically unless blocked by missing authority, incompatible evidence, absent data or a material methodological choice that cannot be resolved from the repository.

---

## Intended interpretation

Step 8 is successful when it produces a defensible decision, not necessarily a more complicated model. Its governing rule is:

> No complexity without a diagnosed weakness, a testable hypothesis, a frozen comparison and evidence that the incremental benefit is real and proportionate.
