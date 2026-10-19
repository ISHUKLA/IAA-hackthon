# Project instructions

## Read before substantive work

1. context.md.
2. what-good-looks-like.md.
3. docs/evidence/competition-sources.md and the linked official pages when a current verification is required.
4. docs/evidence/known-findings.md, docs/plan.md and docs/status.md.
5. The single numbered prompt requested by the user.

Keep original briefs unchanged unless the user requests edits. They contain unverified professional-standard interpretations and outdated status. Record conflicts rather than silently treating every statement as an official rule. Current source evidence establishes facts; the user's latest instructions establish scope. Proposed plan revisions do not count as human approval.

## Current scope

Step 0 is the scaffold, Step 1 historically defined and verified the prediction/scoring/submission contract, Steps 2–3 produced reversible clean-data and claim/target diagnostics. The current requested scope may advance through the numbered Step 4 prompts for chronological-validation contracts, fold membership, feature-availability guards, fold-safe response/reporting views, scoring utilities, framework tests and bounded handoff repairs while preserving raw inputs and prior behavior. Execute only the specifically requested prompt completely, then report its result; do not automatically execute later prompts. Step 4 does not authorize pricing-model training or tuning, broad feature search, 2025 labels or predictions, publishing or submission upload.

Perform routine, reversible work inside the requested scope without repeated permission requests. Ask only for a genuinely missing decision. An unresolved source issue can remain a disclosed assumption where the prompt permits it. Do not invent an answer or human sign-off.

## Data and actuarial rules

- Raw data is read-only and lives outside Git; use IAA_DATA_DIR. Never alter input Parquet files.
- Loss date determines the covered period, with inclusive boundaries. Report and payment dates are different concepts.
- Predict expected net ultimate cost for a policy-period row. Apply exposure once. Incurred-to-date is an observed reference, not observed ultimate.
- Excess already reflected in amounts must not be deducted twice. Future recoveries and unreported losses require explicit treatment later.
- Preserve known audit corrections as evidence to reverify, not silently executed cleaning rules.
- Exclude suspect contacts from the core specification pending timing evidence. Reported-count histories require as-of reporting dates; historical financial valuations are unavailable.
- The official power is 1.5. Score pooling and weights are not established by the available prose. Separate standard-library metric behavior from the competition's unverified implementation.
- Do not claim that cards, SHAP, ensembles or particular software are professionally mandatory without checking the source.

## Engineering and verification

Use Python 3.12 and small modules in src/iaa_hackathon. The scaffold has no numerical runtime dependency. Add only dependencies needed for the current prompt, then lock the tested environment. Use synthetic fixtures for contract tests. Do not fabricate test passes or rely on a zero-test run.

Avoid fake target or training functions. A pending implementation must be explicit and fail clearly if invoked. Keep original and inferred quantities distinct in schemas, logs and names. Do not silently clip invalid predictions or relabel proxy losses as true ultimate.

Never commit raw data, row-level outputs, credentials, archives or local environment files. Do not push, publish, submit, send messages or change licences unless the user requests that action. Do not spawn subagents unless explicitly requested. Use git status and targeted diffs before finishing; preserve unrelated work.

Update docs/status.md, docs/assumptions.md and PROMPT_LOGS.md as appropriate. Human approval fields stay pending until a human actually approves. An AI review is an AI review.

Finish each prompt with: what changed; evidence and command results; unresolved items; and the next prompt number. Do not represent scaffold checks as Step 1 completion.
