# README flow clarification review

Date: 19 October 2026. Scope: documentation restructuring only. No code, configuration, data, model, prediction, submission or external system was changed by this task.

## Sources read

- `context.md`, then `what-good-looks-like.md`, then `AGENTS.md`.
- The previous `README.md` and current status, assumptions, decisions, known-findings, issue and final-readiness evidence.
- `docs/plan.md`, `PROMPT_ALGORITHM.md`, the Step 2–3 guides, Step 4 prompts and Step 5–10 execution contracts.
- Step 1–7 acceptance documents and Step 8–10 acceptance/readiness reports.
- The actual repository tree, `Makefile`, scripts, configurations, `configs/final_model.json`, Step 6 feature results, Step 7 challenger results and Part 1/Part 2 handoff documents.

The attached `IAA_Readme_Flow_Clarification_Codex_Prompt.md` was treated as the user's requested documentation specification, not as evidence that any analytical step ran.

## Changes made

- Replaced the historical/scaffold-led README with a current, evidence-led overview.
- Added a top status block separating execution, mechanical acceptance, scientific limitations, human decisions and Kaggle state.
- Established revised Steps 0–10 as the canonical execution sequence.
- Separated sequential stages from the cross-cutting EDA, AI and guardrail workstreams.
- Added a Mermaid workflow, phase-to-workstream matrix and contributor navigation.
- Explained the prediction unit, metric, data preparation, EDA, feature eligibility, model building versus model choice, AI authority boundary, controls, results and local submission boundary.
- Retained useful local setup/reproduction commands while removing the old scaffold instructions from the primary narrative.

## Numbering conflicts found

The clarification brief refers to an original 12-step planning document and supplies a mapping to revised Steps 1–10. That original 12-step source is not present in this checkout. The repository instead contains `docs/plan.md`, a consolidated ten-section plan, plus `PROMPT_ALGORITHM.md`, where prompts 01–07 are substeps implementing canonical Step 1. The README records this discrepancy and the supplied conceptual mapping without renumbering historical files or claiming the missing source was verified.

## Claims and links still unresolved

- Current official competition pages were not newly retrieved in this documentation-only task. The Step 10 rules-access failures and prior dated extracts remain the source-status record.
- Current deadline, deliverables/Part 1 timing, submission limits, final-entry rules and exact scorer pooling/weighting remain unresolved.
- The frozen response is an observed-incurred snapshot proxy, not observed ultimate; the ultimate bridge, monetary IBNR, recovery/excess basis and several repair-adoption choices remain pending.
- Human actuarial review, upload authorisation and final-entry selection remain pending.
- The final paginated report and timed video do not exist. Part 2 has not run.
- Step 10's prior controlled package inventory predates this README rewrite. It must be regenerated and reaccepted before anyone relies on that inventory as the current documentation package; the frozen candidate itself was not changed.

## Checks actually run

- README relative-link resolver: **20 local links checked, 0 missing**.
- Frozen-claim cross-check against `configs/final_model.json`: **passed** for model ID, response version and expected row count; the README candidate hash matches the Step 9/10 evidence.
- `git diff --check -- README.md docs/readme-review.md`: **passed**.
- Private-path, private-key, password and token pattern scan of both changed documents: **passed; no match**.
- Numbering/stale-reference search: expected references to Steps 0–10 and the explicit statement that there is no automatic Step 11 remain; no later implementation step is claimed.
- `make check PYTHON=.venv/bin/python`: **failed** at the tracked-file policy because `reports/d2_summary.csv`, committed separately at the user's earlier request, matches the repository-wide `*.csv` prohibition. Compilation did not run after that fail-fast check. This documentation task does not remove the requested published file or weaken the checker.
- The skipped compilation component was then run directly with `.venv/bin/python -m compileall -q src scripts`: **passed**.
- Scope review: this task changed `README.md` and added `docs/readme-review.md`; no implementation, configuration, data, model or prediction file was edited.

No model, submission-generation or external command was run for this review.

## Next implementation action

There is no automatic Step 11. The next substantive action is human resolution of current official rules and the target/financial-basis/repair/model decisions in `docs/part1/human-review-checklist.md`. Any change to the response, features, model or predictions returns to the relevant earlier step and requires a new Step 9 candidate.
