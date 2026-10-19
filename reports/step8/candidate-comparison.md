# Step 8 candidate comparison and decision

Date: 19 October 2026. Decision: **`retain_benchmark`**. The tested contents curvature term produced a tiny primary gain below its preregistered threshold and an interval including zero; it was not promoted. The retained benchmark remains the selected S6 GLM for every line.

Candidate `contents_train_quantile_tent_glm` adds one numeric feature and exactly one regression coefficient to the contents model. Its triangular basis acts on log1p repaired sum insured, with knots at training quantiles 20/50/80%. Missing sum insured contributes neutral zero to the new basis while its original S6 missingness/imputation remains. All original features, alpha=1, log link, power=1.5, solver/tolerance, train-only preprocessing and exposure formulation are unchanged. Motor/buildings predictions are unchanged bit-for-bit. This tests one prospective, observed weakness with no blend, feature search or new response construction.

| Fold | Scope | Benchmark mean deviance | Candidate mean deviance | Benchmark D² | Candidate D² | Benchmark A/E | Candidate A/E |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F2023 | pooled | 103.49608782239278 | 103.49446460865775 | 0.11345157013436835 | 0.11346547459799017 | 1.0499309465855395 | 1.0499398080223863 |
| F2023 | motor | 120.7492256666021 | 120.7492256666021 | 0.08025650973866305 | 0.08025650973866305 | 1.0353644589317161 | 1.0353644589317161 |
| F2023 | buildings | 120.71310568539245 | 120.71310568539245 | 0.06125020062587405 | 0.06125020062587405 | 1.0664407451683784 | 1.0664407451683784 |
| F2023 | contents | 63.19437072682378 | 63.18895250293946 | 0.04568194498645772 | 0.04576376728834064 | 1.0901257656601593 | 1.0902345316070787 |
| F2024 | pooled | 99.43930802654187 | 99.43975136244805 | 0.08980138282838457 | 0.0897973248382723 | 0.9088900586803975 | 0.9089009678811909 |
| F2024 | motor | 108.63384331146969 | 108.63384331146969 | 0.0466271755419132 | 0.0466271755419132 | 0.8034309705954918 | 0.8034309705954918 |
| F2024 | buildings | 124.01118612127274 | 124.01118612127274 | 0.0566901016735023 | 0.0566901016735023 | 1.0633389612673916 | 1.0633389612673916 |
| F2024 | contents | 62.834458250770666 | 62.83593892190203 | 0.052262099399323914 | 0.052239766300756996 | 1.0339037466968584 | 1.0340452339885993 |

| Fold | Model | Reference total CU | Predicted total CU | Total deviance | Predicted cost/exposure |
| --- | --- | ---: | ---: | ---: | ---: |
| F2023 | benchmark | 199679641.86 | 190183594.93962377 | 64825292.08799483 | 380.6381099675485 |
| F2023 | candidate | 199679641.86 | 190181989.80006912 | 64824275.37995583 | 380.6348974018878 |
| F2024 | benchmark | 175536961.49 | 193133327.63795352 | 62267900.29314025 | 386.5218118521741 |
| F2024 | candidate | 175536961.49 | 193131009.53034273 | 62268177.905651346 | 386.5171725744029 |

Paired uncertainty (200 canonical customer-cluster bootstrap replicates, seed 20261019):

| Fold | Mean deviance gain (benchmark minus candidate) | 95% interval | D² gain | D² 95% interval |
| --- | ---: | --- | ---: | --- |
| F2023 | 0.0016232137350158462 | [-0.0034745331623198534, 0.00713026360845987] | 1.3904463621699008e-05 | [-2.9762882678781413e-05, 6.107790293924952e-05] |
| F2024 | -0.000443335906177034 | [-0.006596647975162742, 0.006198779633152797] | -4.057990112291959e-06 | [-6.038115091627987e-05, 5.6739339424418375e-05] |

The primary gain 0.0016232137350158462 is far below the declared 0.060400893187577284 threshold; the confidence interval crosses zero. The reused challenge has a small negative gain (-0.000443335906177034), also with an interval crossing zero. Its tiny loss passes the predeclared no-material-regression tolerance only; it is not evidence that a positive gain replicated. These fixed-prediction intervals exclude model/hypothesis-selection and target-assumption uncertainty.

Contents risk-band effects:

| Fold | Training insured-quantile band | Mean deviance gain | Benchmark A/E | Candidate A/E |
| --- | ---: | ---: | ---: | ---: |
| F2023 | 1 | -0.02023712915295306 | 1.0711298572819599 | 1.0908676900902663 |
| F2023 | 2 | -0.022414057616913396 | 1.0052196879471405 | 1.0035627139042191 |
| F2023 | 3 | 0.08021939026949809 | 1.1267034325670326 | 1.0954507558586546 |
| F2023 | 4 | 0.011093961736719393 | 1.2071679337716243 | 1.2081980022756273 |
| F2023 | 5 | -0.02136088765590216 | 1.0337524406117216 | 1.0444704427590141 |
| F2024 | 1 | 0.0018797594286255048 | 0.9860408324183151 | 1.0081998059272435 |
| F2024 | 2 | 0.00952873185798353 | 1.0864459678106004 | 1.083914469334844 |
| F2024 | 3 | 0.0065605658204006545 | 0.9797337260233556 | 0.9462661020711005 |
| F2024 | 4 | -0.005564457513514753 | 1.1008794574950036 | 1.102073124566357 |
| F2024 | 5 | -0.017046426861270447 | 1.0104500275808939 | 1.0232161795082244 |

The third primary band improves while several other bands worsen; the fourth-band underprediction is largely unchanged. A small fitted curve therefore does not resolve the broader residual pattern. Overall and major-line A/E remain within the predeclared 0.01 extra absolute-error tolerance. Prediction-decile, exposure-band, new/returning and categorical-risk tables for both models are in the fold diagnostic JSONs.

Tail checks:

| Fold | Sensitivity | Benchmark mean deviance | Candidate mean deviance |
| --- | --- | ---: | ---: |
| F2023 | exclude top 10 observed rows | 100.25671357776969 | 100.25509033811903 |
| F2023 | subtract largest contents claim amount | 103.45080664644864 | 103.44926723538482 |
| F2023 | top_1pct_observed | 3410.783312141453 | 3410.7214044932216 |
| F2023 | excluding_top_1pct_observed | 70.08672182105654 | 70.08570758519359 |
| F2023 | top_1pct_predicted | 170.37765880814743 | 170.37765880814743 |
| F2024 | exclude top 10 observed rows | 98.02977124475879 | 98.03021458774496 |
| F2024 | subtract largest contents claim amount | 99.40432158071381 | 99.40476969735296 |
| F2024 | top_1pct_observed | 3019.5769460071015 | 3019.6448350054166 |
| F2024 | excluding_top_1pct_observed | 69.94249244629019 | 69.94225450188962 |
| F2024 | top_1pct_predicted | 152.73000635972795 | 152.73000635972795 |

The primary tiny gain persists in the declared extreme-loss sensitivities and two insured bands, so the breadth check passes; it still fails materiality and uncertainty. All claims remain in the primary response. The largest contents amount was 111,900 CU in 2023 and 89,086.41 CU in 2024; sensitivities subtract only those linked amounts without fitting altered targets. Prediction ratios to benchmark range 0.972704–1.099505 in 2023 and 0.966571–1.168390 in 2024; totals remain within ±5% and all predictions are strictly positive and finite.

| Promotion gate | Status | Evidence / interpretation |
| --- | --- | --- |
| 1 | fail | Gain below 0.060400893187577284 and primary CI includes zero. |
| 2 | pass | Gain persists after declared tail sensitivities and in two contents insured bands. |
| 3 | pass | Overall and line A/E-error deterioration stays within 0.01. |
| 4 | pass | Positive finite predictions; declared total and per-row ratio bounds pass. |
| 5 | pass | Frozen provenance, IDs, train-only knots, one added coefficient, unchanged other lines and reloads pass. |
| 6 | pass | One added coefficient and two fits; runtime/memory remain inside the declared budget. |
| 7 | pass | Single reused challenge loss is within the declared uncertainty tolerance, without a positive replicated gain. |

Runtime was 51.11879413295537 seconds including diagnostics; peak process memory was 3016339456 bytes (2.809 GiB). The two actual contents fits took 3.3643989990232512 and 5.521892478922382 seconds, converged in three Newton iterations, and each saved fitted artifact is 10057 bytes. Their standardized new-feature coefficients were 0.02058460317265938 and 0.025354356462243807; these are not currency effects or causal parameters. Benchmark peak memory was not measured; historical stage runtimes are not a controlled speed comparison.

The configuration, benchmark and scorer were frozen before fitting; the primary model and unchanged refit rule were saved before the first candidate evaluation on 2024. Refit knots use training-only 2021–2023 predictors rather than 2024 outcomes. The candidate, not just the retained benchmark, passed full reload and exact-coverage checks.

Run fingerprint: `ab0e918c38e92818a1513c4176a4d205731df8a67be742fa7c376ba783fe1865`. Exact feature lists, hashes, software, predictions, model objects, bootstrap/segment/tail diagnostics, timing and event records are under ignored `outputs/step8/contents-tent/`; final decision is `outputs/step8/decision.json`.

Judgement: preserve the simpler benchmark and keep this negative experiment as evidence. No final architecture, repair/financial assumption or actuarial sign-off is approved by this automated decision. Ultimate/IBNR, recoveries, timing and official scoring weights/pooling remain unresolved. No alternative candidate was tried after seeing these results.

Reproduce from the existing checkout and frozen Steps 5–7 artifacts:

```text
make step8-check PYTHON=.venv/bin/python
make step8-preflight PYTHON=.venv/bin/python
make step8-diagnosis PYTHON=.venv/bin/python
make run-conditional-complexity PYTHON=.venv/bin/python
make step8-acceptance PYTHON=.venv/bin/python
```

Unchanged diagnosis and complete experiments are reused after checksum verification. Next prompt: Step 9; it was not executed.
