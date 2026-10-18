# Prompt 07 — Verify and hand over Step 1

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Provide a concrete, reviewable Step 1 package and a reliable one-command check.

## Procedure
1. Implement make step1-check to validate contract JSON/schema, execute nonzero behavioral tests, run synthetic examples and emit a concise verification summary. Fail if required modules/documents/tests are missing or if collection finds no tests. Separate this from local-data inventory verification.
2. Verify a fresh Python 3.12 environment can install the exact dependency lock and local package. Record actual commands and results. Avoid local absolute paths in the committed lock. State platform limits instead of promising universal byte identity.
3. Update CI with a Step 1 contract/test job that needs no raw data. Keep only read permissions. Verify the workflow's commands locally where possible; do not claim GitHub CI ran until it did.
4. Write docs/step1/acceptance.md mapping each objective to evidence: prediction grain; net basis; ultimate/reference distinction; exposure; fixed metric; submission identity; assumptions; and human decisions still needed.
5. Populate cards only with implemented facts. Update docs/status.md and PROMPT_LOGS.md. Machine verification can be complete while human actuarial acceptance remains pending.
6. Inspect git status/diffs and run the tracked-data check. Provide a suggested commit message and handoff summary. Do not commit, push or upload unless the user requests it.
7. Stop after Step 1. State the later work: actual cleaning, claim linkage/financial reconciliation, maturity modelling, split manifests, baselines and predictive training.

## Acceptance
make step1-check genuinely passes on synthetic data with tests collected. Contract and source evidence agree, remaining assumptions are explicit, and actual human acceptance has not been fabricated.
