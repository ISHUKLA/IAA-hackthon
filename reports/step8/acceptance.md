# Step 8 acceptance — completed, benchmark retained

Date: 19 October 2026. Step 8 completed with **`retain_benchmark`**. The one registered candidate was executed and rejected by its materiality/uncertainty gate. This is successful conditional-complexity control, not a successful model promotion or human actuarial approval.

The newly supplied `IAA_Step8_Conditional_Complexity_Prompt (1).md` is byte-identical to `prompts/step8/00-conditional-complexity.md`, SHA-256 `c6babe40cf10d16e53958605f1d144fa27824d7d04b68ec7ef9bd5c12fface1c`. Prior blocked-preflight reports and configuration were archived under `reports/step8/history/pre-step7/`; the old decision was copied to ignored `outputs/step8/history/`. Existing S5–S7 code, models, predictions, raw/repaired inputs, briefs and Git identity were preserved.

Actual execution evidence:

- `make step8-preflight PYTHON=.venv/bin/python`: **101 checks passed**, zero failed, ready. This includes repaired identities, matching S4–S7 monetary/exposure views and version aliases, recovered logical membership, unchanged artifacts/config/code, S7 actual acceptance and reproducing all S5/S6/S7 pooled scores. The qualified S6 model settings, exact features, response, folds, scorer and artifact hashes are in `outputs/step8/benchmark-frozen.json`.
- `make step8-diagnosis PYTHON=.venv/bin/python`: real primary-fold residual, calibration, exposure, tail and training-quantile risk analysis completed. Customer-bootstrap bands supported testing the contents intermediate-insured pattern. A conservative materiality threshold was derived from pre-existing paired score variability and registered before fitting; this was not a universal D² threshold.
- `make step8-check PYTHON=.venv/bin/python`: **33 passed**, covering the new refinement/preflight gates plus preserved baseline, reporting cutoff and validation checks. Eighteen tests directly cover Step 8 identity/gate and refinement mechanics.
- `make run-conditional-complexity PYTHON=.venv/bin/python`: one additional contents coefficient, with two train-only fits and a single frozen reused challenge evaluation. The primary mean-deviance gain was 0.0016232137350158462, below 0.060400893187577284, with interval [-0.0034745331623198534, 0.00713026360845987]. The challenge gain was -0.000443335906177034, also consistent with zero. No search or second candidate followed the failed gate.
- `make step8-acceptance PYTHON=.venv/bin/python`: **passed** actual 626,355 F2023 and 626,190 F2024 rows; direct Step 4 scorer agreement, exact IDs and metadata, positive finite period predictions, full model reloads, registered-before-fit and frozen-before-challenge chronology, train-only knots, one added coefficient, unchanged base features/settings, bitwise-unchanged other lines and all upstream/config/code/artifact identities. The independent validator also saves baseline-ranked high-prediction-tail checks as an acceptance diagnostic, after selection.
- `make check PYTHON=.venv/bin/python`: scaffold and compilation passed. `PYTHONPATH=src .venv/bin/python -m pytest -q`: **140 passed**, with one nonfatal Joblib physical-core detection warning. `pip check` reported no broken requirements; all 26 inherited exact dependencies matched `requirements/step7-py312.lock`. No new dependency was installed for Step 8.

Candidate fits converged in three Newton iterations. Primary/challenge fitting took 3.3643989990232512/5.521892478922382 seconds. Whole-experiment runtime including diagnostics was 51.11879413295537 seconds; whole-process peak resident memory was 3,016,339,456 bytes (2.809 GiB). Both saved candidate artifacts are 10,057 bytes. Recorded baseline-stage runtime is not a like-for-like standalone speed comparison; benchmark-only peak memory remains unmeasured.

Promotion gate 1 failed; gates 2–6 passed. Gate 7 passed only its predeclared within-noise/no-material-regression tolerance on the reused challenge, not a claim of a positive replicated improvement. No gate was silently omitted or adjusted after observing results. The decision remains `retain_benchmark` because all applicable gates are required for promotion.

Synthetic outcome-perturbation checks require unchanged fitted features/parameters and predictions; changing outcomes correctly changes the score itself. The prompt's literal suggestion that a score should not change when outcomes change is interpreted as this leakage invariant, not an instruction to ignore the response during scoring. No decomposed model was chosen, so there is no invented peril/frequency–severity reconciliation claim; the whole-book assembly does verify unchanged other-line rows and exact total coverage.

Saved under ignored `outputs/step8/`: benchmark/preflight/diagnosis records, prior blocked-decision history, decision and acceptance, the candidate's fitted models and complete predictions, frozen selection, bootstrap/calibration/risk/tail tables and immutable experiment manifest. The registered gate is `configs/step8_complexity_gate.json`; the comparison and diagnosis reports are under `reports/step8/`. Row-level outputs and fitted objects remain excluded from Git.

Reproduce from the existing checkout with its frozen Steps 5–7 artifacts:

```text
make step8-check PYTHON=.venv/bin/python
make step8-preflight PYTHON=.venv/bin/python
make step8-diagnosis PYTHON=.venv/bin/python
make run-conditional-complexity PYTHON=.venv/bin/python
make step8-acceptance PYTHON=.venv/bin/python
```

Repeating `make run-conditional-complexity PYTHON=.venv/bin/python` returned `reused_verified_run` with the same `retain_benchmark` decision after input/config/code/artifact verification and zero new fits. Changed provenance fails clearly rather than overwriting the completed experiment. `git diff --check`, exact guide comparison and representative output/model Git exclusions passed. The original preflight blockers were resolved and their evidence remains historical. Ultimate loss, monetary IBNR, financial basis, future recoveries, repair/exposure adoption, official score implementation and prospective timing decisions remain pending. Primary exploratory diagnosis and fixed-model bootstrap do not establish an independent temporal validation.

Next prompt: **Step 9**. Step 9, final predictions, submission, commit, push and publication were not performed.
