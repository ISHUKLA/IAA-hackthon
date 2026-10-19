# Step 8 acceptance — blocked at preflight

Date: 19 October 2026. Full Step 8 acceptance has **not** passed. No model experiment, bootstrap, candidate promotion or challenge confirmation was performed.

Actual checks:

- `make step8-check PYTHON=.venv/bin/python`: 11 synthetic tests passed. They cover row alignment, duplicate/wrong identifiers, response/fold/unit mismatches, invalid predictions, held-out-outcome independence of alignment, and fail-closed prerequisite decisions.
- `make step8-preflight PYTHON=.venv/bin/python`: exited **2**, recording `decision: blocked`, 40 passing evidence checks, one failed readability check and four untestable saved-membership checks. Missing Step 7 evidence is an additional prerequisite blocker, not a passing gate. Zero candidate fits.
- `make check PYTHON=.venv/bin/python`: scaffold and source compilation passed.
- `PYTHONPATH=src .venv/bin/python -m pytest -q`: **112 passed**, with one nonfatal Joblib physical-core detection warning.
- `cmp` between the supplied guide and `prompts/step8/00-conditional-complexity.md`: byte-for-byte match. Prompt SHA-256: `c6babe40cf10d16e53958605f1d144fa27824d7d04b68ec7ef9bd5c12fface1c`.

The failed file is `outputs/step4/folds/fold-membership.parquet`. Independent pandas and streaming PyArrow reads reported Snappy/Parquet decoding errors. The repaired training table and all four S5/S6 GLM held-out prediction files remained fully readable. Existing pooled scores were reproduced without refitting. The initial audit was strengthened to continue those independent checks after recording the unreadable membership; it does not suppress the failure.

Reproduce from the checkout root:

```text
make step8-check PYTHON=.venv/bin/python
make step8-preflight PYTHON=.venv/bin/python
```

The second command is intentionally nonzero while prerequisites are blocked. Ignored `outputs/step8/decision.json` records all blockers, 65 artifact hashes, available features and scores, seven untestable promotion gates and the measured audit runtime. Original briefs, raw inputs and all S5/S6 outputs were preserved. No commit, push or upload was performed.

Next prerequisite: Step 7 evidence and a readable, verified frozen Step 4 membership. Next execution after those are resolved: rerun Step 8; do not proceed to Step 9.
