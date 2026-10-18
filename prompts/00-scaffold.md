# Prompt 00 — Establish the repository

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Create or verify Step 0. This is infrastructure, not Step 1 actuarial implementation.

## Procedure
1. Inspect the working directory and git status. If the starter exists, preserve it. If creating from scratch, use the layout described in README.md: root briefs/instructions, prompts/, configs/, docs/evidence/, src/iaa_hackathon/, tests/fixtures/synthetic/, schemas/, scripts/, data/ and outputs/.
2. Read context.md then what-good-looks-like.md. Keep originals unchanged. If absent, report them as missing; do not manufacture replacements from memory.
3. Verify CLAUDE.md points to AGENTS.md and the latter defines the current scope and source precedence.
4. Create/verify pyproject.toml, a standard-library read-only doctor command, .gitignore, scaffold checks and read-only CI. Do not create dummy target, model or scorer functions. Do not add numerical dependencies just to check the scaffold.
5. Use a local virtual environment with Python 3.12. Install the local package. Run make check and the CLI help. Verify IAA_DATA_DIR if it is set. A missing local path is configuration to report, not justification for searching the entire computer.
6. Inspect Git exclusions for a raw Parquet, archive and prediction CSV. Do not add real records as test fixtures. Do not push or choose a licence.
7. Update docs/status.md and PROMPT_LOGS.md with actual results. Leave Step 1 and human review pending.

## Acceptance
The local package installs, help runs, scaffold checks pass, raw inputs/outputs are excluded, and no model/metric implementation is falsely claimed. Scope: Step 0 only. Next: Prompt 01.
