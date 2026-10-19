# Step 7 acceptance and handoff

Step 7 completed locally on 19 October 2026. Real-data implementation acceptance passed; the modelling decision is **`glm_preferred_for_step8`**. Acceptance of executable behavior does not establish actuarial approval or ultimate-loss accuracy.

The supplied guide was saved byte-for-byte as `prompts/step7/00-lightgbm-challenger.md`, SHA-256 `4acb37ec2126af78e801b22e0214b23e9be94350cba3e06c1565a76f6cbe3c5e`. Only the active-scope paragraph of AGENTS.md changed; the original briefs and the previous Step 8 blocked-preflight records were preserved.

Actual commands and results:

- Pinned LightGBM 4.6.0 installed without changing existing numerical dependencies; `pip check` reported no broken requirements and all **26 exact versions** matched `requirements/step7-py312.lock`.
- `PYTHONPATH=src .venv/bin/python scripts/step7_preflight.py` passed. All 16 repaired-output hashes matched; repaired policy/claim identity, S5/S6 response, configuration and feature implementation were verified. S6 saved-model reloads reproduced all 626,355 F2023 and 626,190 F2024 predictions and their recorded scores.
- Frozen folds were recovered deterministically from the same repaired policy input and validation config. The replacement matched original logical digest `f444d8c7f7a91e842a5f2789d212121bb65578d4e1389ce5cf56f3f4eb1a7fa5`, including roles, years and row identities. Its SHA-256 is `2f7cf05e0b41cc92466d7cff4f560b49157dba8b8979c7e355676baa07ca0eaf`. Original corrupted bytes were copied to ignored `outputs/step7/fold-recovery/original-d86ba94648e7a6f3368b5a5580bb1aee93f04d5d307af89eadbb8f30290a0710.parquet.corrupt` and their original SHA-256 was checked before replacement. No random split or changed membership was introduced.
- `make step7-check PYTHON=.venv/bin/python`: **31 passed**. The gate includes 21 new challenger tests plus reporting-cutoff and frozen-validation tests.
- `make run-lightgbm-challenger PYTHON=.venv/bin/python`: completed three conservative primary fits and three frozen challenge refits. No further configurations qualified for the predeclared search budget. Exact features, annual-rate response, square-root exposure weights and one exposure multiplication were preserved.
- `make step7-acceptance PYTHON=.venv/bin/python`: passed all three lines, exact held-out ID coverage, prediction provenance, direct S6 feature equality, Step 4 scorer agreement, positive finite policy-period predictions, selected-model reload equivalence, upstream/config/code/artifact hashes and frozen-round challenge event order. F2024 was evaluated once after selection was frozen. The acceptance artifact is external to the immutable training manifest.
- `make check PYTHON=.venv/bin/python`: scaffold and compilation passed.
- `PYTHONPATH=src .venv/bin/python -m pytest -q`: **133 passed**, with one nonfatal Joblib physical-core detection warning.

Saved under ignored `outputs/step7/`: preflight/recovery evidence, complete candidate and selected predictions, native models and training-only categorical vocabularies, early-stopping/search histories, selected feature lists, frozen-selection record, cluster-bootstrap/calibration/tail/segment diagnostics, native TreeSHAP/importance/dependence artifacts, decision and immutable run manifest. Models and predictions are excluded from Git. Existing S5/S6 artifacts and repaired inputs were unchanged.

The experiment runtime was 84.34725118405186 seconds; whole-process peak memory was 3,525,201,920 bytes. Synthetic determinism and full actual saved-model reload equivalence were verified. Repeating `make run-lightgbm-challenger PYTHON=.venv/bin/python` returned `reused_verified_run` after rechecking provenance and artifact hashes, with the same `glm_preferred_for_step8` decision and zero new fits. A second full training run was not performed merely to duplicate unchanged results. `git diff --check`, configuration/registry/acceptance JSON parsing and representative model/prediction Git exclusions also passed. The exact comparison, uncertainty intervals, calibration and tail limitations are in `docs/step7/lightgbm-results.md`.

Remaining limitations: snapshot costs do not identify ultimate outcomes, historical financial valuations or monetary IBNR. Financial basis, future recoveries, exposure and sum-insured adoption, and official metric weights/pooling remain unresolved. F2024 is reused development evidence. Bootstrap intervals condition on selected models and the provisional response. SHAP and partial dependence describe model behavior and include correlated-feature/sample limitations.

Reproduction, from the existing checkout:

```text
make step7-check PYTHON=.venv/bin/python
make step7-preflight PYTHON=.venv/bin/python
make run-lightgbm-challenger PYTHON=.venv/bin/python
make step7-acceptance PYTHON=.venv/bin/python
```

Next prompt: **Step 8**, using the S6 GLM as the selected benchmark and the completed S7 evidence. The older Step 8 blocked decision is historical and was not rerun or relabelled as accepted. No Step 8/9, blend, final 2025 prediction, submission, commit or push was performed in Step 7.
