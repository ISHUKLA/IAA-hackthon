# IAA AI-assisted hackathon — Part 1 starter

This repository starts with **Step 0: a working scaffold**. The numbered prompts implement **Step 1: the prediction, exposure, scoring and submission contract**. It contains no trained model, constructed ultimate labels or competition prediction file.

## Start locally

Use Python 3.12. From the extracted repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements/step1-py312.lock
python -m pip install --no-build-isolation --no-deps .
make check
make step1-check
export IAA_DATA_DIR="$HOME/Desktop/IAA Hackathon/public"
make doctor
python -m iaa_hackathon inventory
claude
```

If `python3` is not Python 3.12, use your Python 3.12 executable when creating the environment. `make doctor` verifies file presence only; it does not claim to have inspected Parquet contents. Install the data/scoring extras when the corresponding prompt needs them, not to run the scaffold.

Paste into Claude Code:

```text
Read AGENTS.md. Execute only prompts/00-scaffold.md in this repository.
```

Then execute prompts 01 through 07 individually, reviewing each result. See [PROMPT_ALGORITHM.md](PROMPT_ALGORITHM.md). The complete copy-and-paste instructions are in that file and in the individual prompt files.

The root CLAUDE.md imports AGENTS.md for persistent guidance. Other coding tools can read AGENTS.md directly. File instructions guide an agent; they are not security enforcement. Do not enable permission bypasses for this workflow.

## Repository map

| Location | Purpose |
| --- | --- |
| `AGENTS.md`, `CLAUDE.md` | Persistent operating instructions |
| `context.md`, `what-good-looks-like.md` | User's original briefs, preserved unchanged |
| `docs/plan.md` | Revised plan, including explicitly proposed changes to the briefs |
| `docs/evidence/` | Aggregated audit findings, expected metadata/hashes and source references |
| `docs/status.md`, `docs/assumptions.md` | Execution status and unresolved decisions |
| `prompts/00-*.md` through `07-*.md` | Bounded sequential prompts |
| `src/iaa_hackathon/` | Doctor, read-only inventory, fixed metric and submission validator |
| `tests/` | Synthetic contract, metric and submission behavioral tests |
| `configs/`, `schemas/` | Project configuration and validated problem contract/schema |
| `data/`, `outputs/` | Local-only working areas; contents excluded from Git |

Keep the dataset in its existing Desktop folder and point IAA_DATA_DIR at it. No copy is needed. Raw data, row-level predictions and archives are excluded by .gitignore; the repository checker also detects prohibited files in the Git index. Synthetic test fixtures are allowed only under tests/fixtures/synthetic/.

## Commands and honest status

- `make check`: verifies the scaffold, JSON configuration, Python syntax and Git-index file policy. It does **not** validate actuarial targets or metrics.
- `make doctor`: checks whether the eleven expected local files exist.
- `python -m iaa_hackathon inventory`: performs the Prompt 02 read-only Parquet metadata, hash, required-field and key-coverage checks and writes machine-specific evidence under ignored `outputs/step1/`.
- `make step1-check`: validates the problem JSON/schema, required examples, required files and nonzero synthetic contract/metric/submission tests. It does not inspect raw data or validate a model.

The presence-only scaffold uses the standard library. Step 1 dependencies retain compatible bounds in `pyproject.toml`, while `requirements/step1-py312.lock` records the exact environment tested for handoff. Platform-specific wheel byte identity is not promised.

## GitHub handoff

If this directory is not already your Git repository:

```bash
git init -b main
git add .
python scripts/check_repo.py
git diff --cached --stat
git diff --cached
git commit -m "Scaffold IAA Part 1 workflow and prompt sequence"
```

After reviewing the staged files, attach your existing GitHub remote and push. This starter does not create a remote, publish files, accept competition terms, or choose a code licence for you. Original competition data retains its own terms.

## Definition of Step 1 completion

A source-backed, machine-readable prediction contract; a tested fixed-power Tweedie scorer; a tested submission validator; explicit unresolved assumptions; and a reproducible synthetic verification command. Human actuarial acceptance is recorded separately from automated checks. Model training and target development belong to subsequent work.
