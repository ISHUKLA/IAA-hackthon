# Step 9 acceptance — ready for human review

Date: 19 October 2026. Status: `ready_for_human_review`, local snapshot-proxy candidate only. No actuarial approval, official-scorer equivalence, production readiness, Kaggle acceptance or ultimate-loss accuracy is claimed. The file has not been uploaded to Kaggle.

## Selection, inputs and refit

The governing Step 8 decision is `retain_benchmark`, so the frozen `S6_selected_compact_tweedie_glm` is selected. Neither rejected challenger is promoted. Configuration `configs/final_model.json` was frozen before its final production fit; SHA-256 `873a17e390ff319bf14c645703065e04cb38fae33733f901ff28be0251ed408b`, run ID `873a17e390ff319b`.

Response: `repaired_observed_net_incurred_snapshot_2024-12-31`. Training: all 2,409,311 repaired 2021–2024 rows. Scenario: matched open/closed incurred less recorded recoveries, case factor one, no additional monetary IBNR/development/future-recovery/trend allowance. These identity choices preserve the observed proxy; they are NOT estimates that ultimate components are zero. Deduplication, ACT/365 and sum-insured interpretation remain provisional. Raw-claim Step 3 scenarios were not mixed in.

Source/config/code hashes, the complete frozen Steps 5–8 evidence map and all 11 raw input hashes passed before each build. The exact 26-package environment and Python 3.12.11 matched. Integer-minor-unit reconciliation reproduced all policy responses from accepted repaired matched claims, total 741,156,868.43 CU. Test row identity/order and exposure were separately reconciled to each original 2025 test file, then to the sample through a validated one-to-one join.

One final production GLM per line retained every frozen feature and parameter, training-only preprocessing, square-root exposure fitting weights and one inference exposure multiplication. All three converged in three Newton iterations. All saved-model reloads and CSV values matched pre-save predictions exactly, with measured maximum error 0.0 (predeclared tolerance rtol=1e-12, atol=1e-10). No floor, clipping, recalibration, blend, feature change or search was applied.

## Local CSV and mechanical gates

Primary file, relative to repository root:

`submissions/part1_S6_glm_repaired_observed_net_incurred_snapshot_2024-12-31_873a17e390ff319b.csv`

SHA-256: `dfb3e565d97f0a4a597ab3051b6cffd616da5022aaf8da10aa0736db436e6274`.

| Line | Rows | Predicted cost CU |
| --- | ---: | ---: |
| Motor | 254,986 | 106,408,103.14559814 |
| Buildings | 184,155 | 65,758,748.39939484 |
| Contents | 187,498 | 17,387,149.91093321 |
| Overall | 626,639 | 189,554,001.45592618 |

Passed: exactly `row_id,prediction`, no index/extra columns, unique non-null string IDs, exact sample membership and order, raw test prefixes/counts, numeric finite strictly positive predictions, policy-period units, exposure once, saved-model equivalence and independent clean byte-for-byte reproduction. No mechanical gate failed. The independent rebuild began in a new empty directory, read repaired sources anew and performed three independent fits; it reused neither production models nor predictions. Model/schema artifacts also have identical hashes. This is exact reproduction in the tested pinned environment, not a cross-platform guarantee.

## Actual commands and verification

Run from the existing repository with the local official public-data directory supplied as DATA_DIR:

```text
make step9-check PYTHON=.venv/bin/python
PYTHONPATH=src .venv/bin/python -m pytest -q
make check step5-acceptance step6-acceptance PYTHON=.venv/bin/python
make build-final-model build-submission verify-submission reproduce-step9 step9-finalize PYTHON=.venv/bin/python DATA_DIR='/path/to/official/public'
.venv/bin/python -m pip check
git diff --check
```

Results: 65 targeted tests passed; all 161 tests passed, including the 140 previous tests and 21 new final-boundary/provenance cases. Synthetic tests reject duplicate/missing/extra/reordered/non-string IDs, index columns, NaN/Inf/negative/zero/non-numeric/Boolean predictions, annual-rate and double-exposure output, source/model hash mismatch, invalid equivalence shapes and provenance-overwrite regressions. Train-only imputation/category vocabulary, unknown categories, exposure scaling and saved-model reload are exercised. Real S5/S6 acceptance still passed 626,355/626,190 held-out rows. Scaffold compilation and Git index policy passed. `pip check` found no broken requirements. Exact guide comparison and representative CSV/model/reproduction Git exclusions passed.

Final production refit, reconciliation and serialization: 32.09117285790853 seconds; clean end-to-end reproduction including verification: 44.276002740021795 seconds. Whole-stage peak memory was not measured. Nonfatal PyArrow sandbox sysctl cache warnings and Joblib physical-core detection fallback were observed; all commands above completed successfully. No new dependency was installed.

The initial numerical protocol also passed exact reproduction. Review then caught an audit-packaging defect: repeating finalization could rewrite the Git patch referenced by an immutable manifest. All initial generated artifacts and configuration were preserved under ignored `outputs/step9-packaging-v1/`; its original CSV was not overwritten. The final v2 uses content-addressed snapshots and a verified read-only existing-manifest path. It was frozen and rebuilt cleanly; predictions and model hashes are unchanged. This is an AI-caught error with automated verification, not fabricated human oversight.

After adding the acceptance/status documentation, repeating `make step9-finalize` returned `reused_verified_immutable_manifest` with no refitting. The original manifest SHA-256 still matched the status record; every referenced Git snapshot and the CSV hash remained unchanged. This verifies the corrected real rerun path, not only the synthetic regression.

## Financial review and unresolved items

Aggregate and line quantiles, very-small/large predictions, training cohort rates, full-training in-sample totals, inherited holdout calibration, new/returning policies and customers, fixed-model SI sensitivity and financial-reference stresses are in `submission-diagnostics.md` and ignored `outputs/step9/financial-diagnostics.json`.

Total clean test exposure is 500,351.282; predicted cost/exposure is 378.84184227 CU. There are 795 predictions below 1 CU, linked to fractional exposure; no prediction exceeds 10,000 CU. Same-test-row refitting changes motor/buildings/contents totals by -5.4755%/+1.2164%/+1.0220% against the F2024 fold models. Motor's 2024 observed rate is 453.82 versus 587.47 CU/exposure in 2023, illustrating why the added immature snapshot can reduce the fitted reference. This is an explanation/review item, not proof of the amount of missing ultimate loss, and no total was forced.

The raw-SI counterfactual extrapolates suspected x1000 unit errors to astronomical values, not credible alternative forecasts. The chosen 730 test repairs account for about 169,719.95 CU of chosen predictions; human adoption still matters. Recorded recoveries change the repaired training reference by 27,501,378.71 CU under competing gross/net definitions. ±20% of accepted case balances gives illustrative training totals 723,123,225.042/759,190,511.818 CU; these are not re-fitted forecasts or established reserve adequacy bounds. Ultimate sensitivity to IBNR, development, recoveries and trend remains unidentified. The retained large BI claim and quarantined claims remain explicitly disclosed.

Inherited S6 F2023 D²/A/E is 0.1134515701/1.0499309466; F2024 is 0.0898013828/0.9088900587 (motor A/E 0.803431). These snapshot-proxy, reused-development-fold results are not 2025 calibration or fully prospective monetary validation. Official pooling, weights and scorer implementation remain unresolved.

Fresh current Kaggle checks failed for all four pages and the prior evaluation route; no stale deadline, daily limit or final-entry limit is carried forward as current. See `official-rules-check.json`. No terms were accepted or organiser contacted. No unexplained critical mechanical/distribution alert remains for the chosen local specification; these disclosed financial and rules uncertainties still require human review before any separate upload decision. Human review and final Kaggle-entry selection remain `pending`.

## Changed files and reproducibility handoff

Step 9 added its prompt, frozen final config, two final pipeline/review modules, command script, adversarial tests and `reports/step9/` evidence/decision/acceptance records. It updated only AGENTS.md's active-scope paragraph, added Make targets and appended current model/status/assumption/decision/prompt/source records. Pre-existing Step 7/8 uncommitted changes, original briefs, raw inputs, Git identity and origin were preserved. Generated models, row-level CSVs, clean reproductions and manifests remain ignored. No commit, push, publication or upload occurred; no external CI result is claimed.

Independent clean reproduction from the current checkout and controlled repaired/frozen evidence:

```text
make reproduce-step9 PYTHON=.venv/bin/python DATA_DIR='/path/to/official/public'
```

The immutable manifest is `outputs/step9/submission-manifest.json`; status is `outputs/step9/status.json`. Its dirty Git snapshot is truthful at generation time; later acceptance/status documentation is a later state, not retroactively substituted into that snapshot. Next action: human review, not another automatic numbered prompt. Stop after Step 9. The file has not been uploaded to Kaggle.
