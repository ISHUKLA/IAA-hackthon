# Decision log

## S9-001 — frozen S6 local proxy candidate, 19 October 2026

Step 8 `retain_benchmark` deterministically selects `S6_selected_compact_tweedie_glm`; no rejected challenger, new feature, blend, response change or recalibration is adopted. The frozen final config uses all 2021–2024 repaired rows and the exact observed snapshot response. Three full-data fits and an independent clean build produced identical saved artifacts and a 626,639-row sample-order CSV; total 189,554,001.45592618 CU, SHA-256 `dfb3e565d97f0a4a597ab3051b6cffd616da5022aaf8da10aa0736db436e6274`. Status is `ready_for_human_review`, not actuarially approved or verified ultimate.

All 161 tests and 65 targeted checks passed. The first numerical packaging run was preserved after AI review caught an immutable-audit overwrite risk; the corrected v2 was frozen before rebuilding and preserves the same model/CSV bytes. No model selection changed. Financial diagnostics, exact commands and limitations are in reports/step9/acceptance.md; structured AI-direction evidence never invents human approval. Financial/repair/ultimate assumptions and fresh Kaggle rules access remain unresolved; no upload, final-entry selection, commit or push is authorised. Next action is human review; stop after Step 9.

## S8-001 — stop at blocked preflight, 19 October 2026

Decision: `blocked`. Basis: the Step 8 execution contract explicitly requires Steps 5–7 evidence, and local Step 7 artifacts are absent. The saved Step 4 membership also fails Snappy/Parquet decoding on two independent read paths. The S6 GLM is the best available S5/S6 model, but cannot be qualified against an absent Step 7 challenger or fully reconciled to unreadable saved membership.

Action: preserve the existing artifacts; capture hashes and independent S5/S6 score verification; fit zero candidates and leave numerical promotion thresholds unset. Record all seven promotion gates as not testable. Resolve the two prerequisites before resuming Step 8. This is an automated/AI execution decision; human actuarial review and the existing financial/repair assumptions remain pending.

Evidence: `reports/step8/acceptance.md`, `reports/step8/benchmark-diagnosis.md`, `reports/step8/candidate-comparison.md`, ignored `outputs/step8/decision.json`.

## S7-001 — retain the S6 GLM after the bounded challenger, 19 October 2026

Decision: `glm_preferred_for_step8`. The Step 7 preflight recovered the original frozen fold membership exactly and verified every S6 saved-model prediction. Phase A tested the identical S6 features using conservative per-line LightGBM; each primary line fit was worse, so the predeclared search rule skipped additional candidates. F2023 pooled D² changed from 0.11345157013436835 to 0.10808390601607543 and material motor calibration deteriorated. Frozen F2024 D² improved from 0.08980138282838457 to 0.09513892935566604, but that reused challenge cannot override the primary selection rule.

The primary customer-cluster bootstrap interval includes zero, and removing only the largest BI amount reverses the small score ordering. This does not prove universal GLM superiority; it fails to justify promoting the bounded LightGBM challenger. Retain all primary claims, the GLM benchmark, negative challenger results and uncertainty. No blend, target adjustment or F2024 retuning was performed. Exact results, gates, native explanations and resource measurements are in `docs/step7/lightgbm-results.md`; real-data acceptance passed and 133 tests passed.

The earlier S8-001 record is preserved. Its two prerequisite conditions were addressed during this separately requested Step 7; Step 8 has not been rerun. Human actuarial review remains pending.

## S8-002 — retain the benchmark after one curvature test, 19 October 2026

Decision: `retain_benchmark`, completed Step 8. Preflight passed 101 checks and froze the S6 GLM using verified Steps 5–7 evidence. The original blocked reports/configuration are archived under `reports/step8/history/pre-step7/`; the old decision remains under ignored `outputs/step8/history/`.

A primary-fold contents intermediate-insured residual pattern justified one training-quantile curvature basis and coefficient. The uncertainty-scaled pooled materiality threshold was registered as 0.060400893187577284 before fitting. Actual gain was 0.0016232137350158462 with interval [-0.0034745331623198534, 0.00713026360845987]; the reused challenge gain was -0.000443335906177034. Gate 1 therefore failed. Gates 2–6 passed and gate 7 passed only its within-noise/no-material-regression tolerance, not a positive replication claim.

Retain all S6 core models and features. Do not adopt the tested basis or try another candidate in this step. The two actual fits, exact common rows, train-only transformations, copied other-line predictions and reloads passed real acceptance; 140 tests passed. Evidence and operational gate judgements are separated in `reports/step8/candidate-comparison.md`, with run fingerprint `ab0e918c38e92818a1513c4176a4d205731df8a67be742fa7c376ba783fe1865`. Financial assumptions and human actuarial review remain pending. Next: Step 9, not executed here.
