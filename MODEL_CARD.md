# Model Card — Steps 5–9, selected GLM and local proxy candidate

## Intended use and response

The implemented models compare simple pricing references on chronological policy folds. The response is repaired observed net incurred valued at 31 December 2024 and is labelled `retrospective_snapshot_proxy`; it is not observed ultimate. Scoring is provisional pooled, unweighted policy-period Tweedie D² at power 1.5.

## Models and exposure

B0 is the training mean; B1 is a training line loss rate times `exposure_clean`; B2 is a conditional supplied-premium comparator; B3 is one compact Tweedie GLM per line. B3 models annual rate with `sqrt(exposure_clean)` training weights and multiplies predicted rate by exposure exactly once. Preprocessing is fitted only on the fold training rows. IDs, outcome fields, contacts, renewal decision, current monetary history, weather and telematics score are excluded.

S6 retains motor age nonlinearity/missingness, buildings log-sum-insured/occupancy-security, and contents log-sum-insured/household-use/security-value blocks. Sum-insured adoption remains a human decision. Motor vehicle/mileage and buildings construction interaction did not improve the primary fold and were rejected.

## Validation and limitations

F2023 is the main fold; F2024 is the frozen recent-year challenge. S5 B3 pooled D² was 0.108781/0.085145; S6 selected D² was 0.113452/0.089801. F2024 S6 A/E was 0.908890, driven particularly by returning policies (0.897049 versus 1.021134 for new policies). The selected S6 candidate also beats S5 after a separate fixed-prediction sensitivity removes the largest linked claim amount from each fold, but those adjusted scores are not alternative targets. These comparisons do not establish ultimate accuracy because historical financial valuations, monetary IBNR, future recoveries and final financial basis are unavailable. Human actuarial approval is pending. No ensemble or submitted prediction exists.

The earlier Step 8 preflight on 19 October 2026 was blocked by then-absent Step 7 evidence and unreadable Step 4 membership. Its historical record is preserved in `reports/step8/history/pre-step7/`; Step 7 recovered the exact logical membership with original-byte preservation and supplied the challenger evidence. The subsequently completed Step 8 is documented below. F2024 was already inspected in S5–S7 and is a reused development challenge.

## Step 7 challenger and decision

LightGBM 4.6.0 used the exact selected S6 features with training-only category vocabularies, native numeric missingness, Tweedie power 1.5, the same rate/exposure formulation, deterministic seeds and four CPU threads. The conservative 15-leaf/1,000-minimum-leaf/L2=10 candidate selected 154/38/42 rounds for motor/buildings/contents. Additional predeclared configurations were skipped because none of these primary fits improved S6.

F2023 LightGBM mean deviance/D² was 104.1227114994232/0.10808390601607543 versus GLM 103.49608782239278/0.11345157013436835. F2024 was 98.85618042865379/0.09513892935566604 versus 99.43930802654187/0.08980138282838457. F2023 A/E worsened to 1.115303 (motor 1.121219); F2024 A/E improved to 0.961082. The primary paired customer-bootstrap mean-deviance gain interval [-2.217545, 0.316509] does not establish improvement. Largest-loss sensitivities change the ordering, so the original large claim remains important and stays in primary results.

Decision: `glm_preferred_for_step8`. This retains the transparent S6 benchmark without claiming statistically proven universal superiority. All 133 tests and real-data acceptance passed. Native TreeSHAP, importance, partial dependence and residual/calibration tables were saved; their small deterministic sample and correlated-feature counterfactual limitations are disclosed. Runtime was 84.35 seconds, whole-process peak memory 3.283 GiB. See `docs/step7/lightgbm-results.md` and `docs/step7/acceptance.md`.

## Step 8 conditional complexity

The verified benchmark remains the S6 GLM. Primary-fold contents A/E exceeded one in intermediate training-quantile sum-insured bands, motivating exactly one additional log-insured curvature basis and coefficient. Knots and all preprocessing were learned only from each fold's training rows; the original GLM settings, response/exposure convention and features were retained, with motor/buildings predictions unchanged bit-for-bit.

The preregistered pooled mean-deviance gain threshold was 0.060400893187577284, derived from the prior contents paired score variability. Actual F2023 gain was 0.0016232137350158462 (D² from 0.11345157013436835 to 0.11346547459799017); its 95% customer-bootstrap interval [-0.0034745331623198534, 0.00713026360845987] included zero. F2024 gain was -0.000443335906177034 (D² from 0.08980138282838457 to 0.0897973248382723). All primary claims were retained, and the tiny gain was not concentrated solely in the declared largest-loss sensitivities.

Decision: `retain_benchmark`; the new feature is not adopted. Promotion gate 1 failed. The other gates passed their predeclared checks, with challenge tolerance passing only as no material regression, not replicated improvement. Whole-run time was 51.12 seconds with 2.809 GiB peak memory; two contents fits converged and full reload/coverage/provenance acceptance passed. All 140 tests passed. Risk-bin diagnosis and bootstrap are conditional exploratory evidence and do not resolve financial/maturity uncertainty. See `reports/step8/benchmark-diagnosis.md`, `candidate-comparison.md` and `acceptance.md`.

## Step 9 controlled local candidate

Step 8's frozen S6 GLM was retained without tuning, extra features, blending or recalibration. Configuration `step9-frozen-S6-observed-proxy-v2-immutable-audit` pins the exact response `repaired_observed_net_incurred_snapshot_2024-12-31`, repaired claim universe, features, preprocessing, parameters, environment and all 2021–2024 training rows. Three full-training GLMs converged in three iterations and saved/reloaded with exactly equal predictions. Production refit including reconciliation/serialization took 32.0912 seconds; the isolated clean build took 44.2760 seconds including verification, with identical CSV bytes. These timings are not like-for-like model speed comparisons.

The local 2025 candidate has 626,639 exact sample-order rows, strictly positive finite policy-period costs, one exposure multiplication and no floor. Total is 189,554,001.45592618 CU (motor 106,408,103.14559814; buildings 65,758,748.39939484; contents 17,387,149.91093321). CSV SHA-256 is `dfb3e565d97f0a4a597ab3051b6cffd616da5022aaf8da10aa0736db436e6274`. It is a snapshot-proxy file, NOT verified ultimate predictions. No 2025 calibration/score is possible without outcomes; inherited F2023/F2024 calibration remains as above.

The same-test-row full refit changes motor/buildings/contents totals by -5.4755%/+1.2164%/+1.0220% versus the F2024 fold model, consistent with the disclosed observed-cohort differences, not grounds for an automatic adjustment. The fixed-model raw-SI counterfactual produces astronomical extrapolations; it is not a credible alternative forecast and reinforces review of the provisional unit repairs. Financial/maturity/repair assumptions and current live Kaggle rules remain unresolved. Human review/final-entry selection stay pending. Code-review caught an audit-overwrite risk after an initial exact run; original artifacts were preserved and v2 adds immutable, content-addressed provenance with a regression test, without changing numerical outputs. See reports/step9/ for decisions, diagnostics, source access and actual acceptance. No upload, commit or push was performed in Step 9.
