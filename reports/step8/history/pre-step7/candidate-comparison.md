# Step 8 comparison — no candidate fitted

Date: 19 October 2026. Decision: `blocked`. No Step 8 candidate has been registered, selected, fitted or promoted. The table below rescored the saved predictions using the current repaired row responses and scorer; it is prior-model evidence only. Local pooled unweighted power-1.5 scoring remains provisional relative to the unavailable official scorer implementation.

| Available model | Fold | Rows | Mean deviance | D² | Reference total CU | Predicted total CU | A/E |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S5 compact GLM | F2023 | 626355 | 104.04128451488587 | 0.10878141030642252 | 199679641.86 | 191569474.42917788 | 1.0423353848779306 |
| S6 selected GLM | F2023 | 626355 | 103.49608782239278 | 0.11345157013436835 | 199679641.86 | 190183594.93962377 | 1.0499309465855395 |
| S5 compact GLM | F2024 | 626190 | 99.9479879747196 | 0.08514527857139687 | 175536961.49 | 194230341.07484275 | 0.903756645427299 |
| S6 selected GLM | F2024 | 626190 | 99.43930802654187 | 0.08980138282838457 | 175536961.49 | 193133327.63795352 | 0.9088900586803975 |
| Step 7 challenger | Both | — | Unavailable | Unavailable | — | — | — |
| Step 8 candidate | Both | — | Not run | Not run | — | — | — |

The following S6 line results are copied from the existing experiment results and were not separately rescored in Step 8:

| Fold | Line | Mean deviance | D² | A/E |
| --- | --- | ---: | ---: | ---: |
| F2023 | motor | 120.7492256666021 | 0.08025650973866305 | 1.0353644589317161 |
| F2023 | buildings | 120.71310568539245 | 0.06125020062587405 | 1.0664407451683784 |
| F2023 | contents | 63.19437072682378 | 0.04568194498645772 | 1.0901257656601593 |
| F2024 | motor | 108.63384331146969 | 0.0466271755419132 | 0.8034309705954918 |
| F2024 | buildings | 124.01118612127274 | 0.0566901016735023 | 1.0633389612673916 |
| F2024 | contents | 62.834458250770666 | 0.052262099399323914 | 1.0339037466968584 |

Existing returning/new and large-claim sensitivities remain in `docs/step6/feature-results.md` and ignored `outputs/step6/features/diagnostics.json`. The primary results retain the extreme claim. No new uncertainty interval, decile calibration, exposure-band check or candidate-tail comparison is claimed. Recorded prior runtimes were S5 `36.93257852597162` seconds and S6 `61.88736547995359` seconds; Step 8 fitted zero models and added zero model parameters. Peak memory is unmeasured.

| Promotion gate | Result | Reason |
| --- | --- | --- |
| 1. Material primary-fold improvement | Not testable | No qualified benchmark/candidate or uncertainty-derived threshold |
| 2. Gain not confined to extremes/one segment | Not testable | No candidate predictions |
| 3. Overall and major-line calibration | Not testable | No candidate comparison |
| 4. Plausible totals, tails and metric domain | Not testable | Available S5/S6 prediction domains passed; no candidate exists |
| 5. Leakage, timing, identity, exposure, reproducibility | Not testable | Frozen membership is unreadable and Step 7 provenance is absent |
| 6. Proportionate complexity | Not testable | No candidate or measured incremental cost |
| 7. Frozen challenge confirmation | Not testable | No primary selection; earlier F2024 results are reused evidence |

It would be misleading to record `retain_benchmark` as a successful Step 8 outcome here: required benchmark qualification is incomplete. The judgement is to stop at `blocked`, preserve all prior artifacts and address the two explicit prerequisites.
