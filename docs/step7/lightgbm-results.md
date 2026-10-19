# Step 7 LightGBM challenger results

Date: 19 October 2026. Decision: **`glm_preferred_for_step8`**. The conservative nonlinear challenger did not improve the primary F2023 comparison; the selected S6 GLM remains the handoff benchmark. This is a conditional modelling judgement, not evidence of ultimate-loss accuracy or statistically established GLM superiority.

Phase A used exactly the selected S6 per-line feature lists and derived blocks, without new features. Inputs are the repaired deduplicated claim candidate and `repaired_observed_net_incurred_snapshot_2024-12-31`; repaired case scenarios remain unavailable. F2023 trains 2021–2022 and validates 2023. F2024 trains 2021–2023 and validates 2024; it is a reused development challenge because S5/S6 already inspected it.

The rate response is observed period cost divided by `exposure_clean`, the training weight is square-root exposure, and predicted rate is multiplied by exposure once. Scoring is the unchanged provisional unweighted period-cost Tweedie metric at power 1.5. Training weights are not metric weights.

| Fold | Scope | GLM mean deviance | LightGBM mean deviance | GLM D² | LightGBM D² | GLM A/E | LightGBM A/E |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F2023 | pooled | 103.49608782239278 | 104.1227114994232 | 0.11345157013436835 | 0.10808390601607543 | 1.0499309465855395 | 1.1153033746906709 |
| F2023 | motor | 120.7492256666021 | 121.84933804538612 | 0.08025650973866305 | 0.07187698437643653 | 1.0353644589317161 | 1.1212194773212805 |
| F2023 | buildings | 120.71310568539245 | 121.20205878722281 | 0.06125020062587405 | 0.05744775826768567 | 1.0664407451683784 | 1.1027039406677983 |
| F2023 | contents | 63.19437072682378 | 63.31371060950964 | 0.04568194498645772 | 0.04387975590821469 | 1.0901257656601593 | 1.1231025387555649 |
| F2024 | pooled | 99.43930802654187 | 98.85618042865379 | 0.08980138282838457 | 0.09513892935566604 | 0.9088900586803975 | 0.961082477220798 |
| F2024 | motor | 108.63384331146969 | 106.89426482186474 | 0.0466271755419132 | 0.061893751844899425 | 0.8034309705954918 | 0.8664611008344552 |
| F2024 | buildings | 124.01118612127274 | 124.32875904010494 | 0.0566901016735023 | 0.05427443509418339 | 1.0633389612673916 | 1.0948797927321858 |
| F2024 | contents | 62.834458250770666 | 62.938381943032255 | 0.052262099399323914 | 0.05069460881106125 | 1.0339037466968584 | 1.0623967196518633 |

| Fold | Model | Reference total CU | Predicted total CU | Total deviance | Predicted cost/exposure |
| --- | --- | ---: | ---: | ---: | ---: |
| F2023 | glm | 199679641.86 | 190183594.93962377 | 64825292.08799483 | 380.6381099675485 |
| F2023 | lightgbm | 199679641.86 | 179036167.54982126 | 65217780.96122122 | 358.3273754691184 |
| F2024 | glm | 175536961.49 | 193133327.63795352 | 62267900.29314025 | 386.5218118521741 |
| F2024 | lightgbm | 175536961.49 | 182645054.56140196 | 61902751.62261871 | 365.5314091996159 |

The scored memberships contain 626,355 F2023 and 626,190 F2024 rows, with exact GLM/challenger ID equality. The saved models reload to the same period-cost predictions. The original frozen fold logical digest was recovered exactly: `f444d8c7f7a91e842a5f2789d212121bb65578d4e1389ce5cf56f3f4eb1a7fa5`; the unreadable original bytes were retained under ignored `outputs/step7/fold-recovery/`.

Configuration and search: native CPU LightGBM 4.6.0, four threads, deterministic seeds 20261019, learning rate 0.05, maximum 500 rounds, 40-round primary-fold early stopping, and 127 bins. The conservative reference has 15 leaves, minimum 1,000 rows/leaf, L2=10 and L1=0. Two additional configurations (31 leaves/500 minimum/L2=20; 7 leaves/2,000 minimum/L2=30/L1=1) were predeclared, but were not attempted because none of the conservative line fits improved the GLM. This follows the predeclared early search stop rather than using the entire budget. Phase B was not run.

| Line | Tried configuration | Selected rounds | Primary fit seconds | Saved model bytes |
| --- | --- | ---: | ---: | ---: |
| motor | conservative | 154 | 8.540561074973084 | 280736 |
| buildings | conservative | 38 | 3.18368469690904 | 71335 |
| contents | conservative | 42 | 2.8149978820001706 | 78862 |

The full experiment, including reloads, explanations and diagnostics, took 84.34725118405186 seconds. Peak process resident memory was 3525201920 bytes (3.283 GiB); this is the whole process peak, not incremental per-fit memory. The three selected round counts were frozen before the first LightGBM challenge-row read and refitted without challenge early stopping. The event order and selection SHA-256 are preserved in the immutable manifest. No boosting convergence claim beyond the recorded early-stopping rule is made.

Paired uncertainty uses 200 customer-cluster bootstrap replicates on fixed predictions, with canonical `customer_id_clean` grouping and seed 20261019. F2023 mean-deviance gain (GLM minus LightGBM) was -0.6266236770304305 with 95% interval [-2.2175450862003396, 0.3165089302329033]; D² change was -0.005367664118292982, interval [-0.018995511383008968, 0.0027112183758864696]. F2024 gain was +0.583127597888087, interval [0.4076715161860334, 0.8117194759003471]; D² change was +0.005337546527281486, interval [0.003731542964817709, 0.007429918401066914]. These intervals condition on the selected models and snapshot response; they do not include model-search or financial-assumption uncertainty and are not independent temporal validation.

Calibration and stability: F2023 pooled A/E deteriorated from 1.049931 to 1.115303; motor moved from 1.035364 to 1.121219 and failed the predeclared 0.05 maximum increase in absolute A/E error. F2024 pooled A/E improved from 0.908890 to 0.961082, mainly from motor, while buildings and contents deviance still deteriorated. The primary loss-cost direction did not persist across years, so the better reused challenge does not justify replacing the primary-fold selection. Prediction-decile, line, exposure-band, returning/new, cover/occupancy/tenure and high-prediction-tail tables are saved in each fold diagnostic JSON.

Returning-customer F2023 mean deviance moved from 106.832378 to 107.607790; new-customer deviance moved from 85.048990 to 84.852929. The corresponding F2024 comparisons were 103.243766 to 102.585041 and 78.343182 to 78.179252. These segment differences qualify the pooled result; they do not establish customer-level causal effects.

Tail sensitivity: the 11,894,276.93 CU F2023 bodily-injury claim remains in primary scoring. Subtracting only that claim amount from its linked row, with all predictions held fixed, changes GLM/LightGBM mean deviance to 101.08833106349051/100.94457004388717. Excluding the top 1% observed-loss rows also favours LightGBM (70.08672182105654 versus 68.66489136567711), whereas their retained top-1% tail deviance is worse (3410.783312141453 versus 3614.1921790209335). This demonstrates influential tail concentration, not permission to remove claims or change the response. The F2024 top-observed tail also worsens despite the pooled improvement. High-prediction-tail and largest-BI sensitivity tables remain available for both folds.

| Predeclared decision check | Result |
| --- | --- |
| primary_paired_ci_positive | fail |
| challenge_direction_positive | pass |
| major_line_calibration | fail |
| gain_outside_top_1pct | pass |
| gain_after_largest_BI_sensitivity | pass |

The decision retains the GLM because primary improvement and material-line calibration criteria failed. Bootstrap uncertainty does not prove the GLM is universally better; it fails to establish a credible benefit from this bounded LightGBM challenger. No weight blend, model-family expansion or F2024 retuning was performed.

Explanations: split/gain importance, native TreeSHAP for 256 fixed held-out rows per line, verified contribution additivity on the log annual-rate scale, and five-point partial-dependence tables were saved. This uses LightGBM’s native contribution calculation without installing the absent standalone SHAP package. Motor importance is led by driver age/licensing/mileage; home importance by sum insured and auditable household factors. Age summaries show elevated young/old risk and insured-value summaries increase across training quantiles. These describe this fitted model only; importance is not proof of predictive value or causation. The small deterministic sample is not claimed representative, and marginal age/licensing counterfactuals can be implausible when correlated predictors are held fixed.

Unresolved: observed costs are a single-snapshot proxy rather than ultimate labels. Financial basis, monetary IBNR, future recoveries, repair/exposure adoption and official score pooling/weighting remain pending. Weather, telematics score and unsafe history were excluded. No final 2025 predictions or competition submission was generated.

Run fingerprint: `a7469f2c8ab234f97dc8f9baf6e87517631b452722ad8dd6f9648382d7c2aee9`. Exact inputs, code-content/config hashes, software, Git state, artifact checksums, feature lists, search history, event order and measured runtime are in ignored `outputs/step7/manifest.json`.

Reproduce from the repository root:

```text
.venv/bin/python -m pip install -r requirements/step7-py312.lock
make step7-check PYTHON=.venv/bin/python
make step7-preflight PYTHON=.venv/bin/python
make run-lightgbm-challenger PYTHON=.venv/bin/python
make step7-acceptance PYTHON=.venv/bin/python
```

An unchanged complete run is reused only after its input/config/code and artifact hashes match. A fresh run needs a separately saved config with a new output directory; existing completed evidence is not overwritten. Next prompt: Step 8, not executed here.
