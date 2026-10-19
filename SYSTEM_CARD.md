# System Card — Part 1 controls and historical scaffold

## Current implemented workflow through Step 10

The repository now implements source-preserving preparation and repairs, inclusive claim reconciliation, explicitly provisional observed response/reporting diagnostics, fixed chronological folds, baselines, bounded feature/LightGBM/complexity comparisons, frozen S6 full refitting, saved-model reload and exact sample-order CSV verification. Step 10 is a local quality review and controlled inventory/handoff, not another modelling stage. Its Make targets check frozen assets, meaningful adversarial tests, safe aggregate joins, a new isolated exact rebuild, payload hashes and critical blockers. No production artifact or prediction is changed.

Current numerical environment: Python 3.12.11 and the 26 exact distributions in requirements/step7-py312.lock; scoped commands use PYTHONPATH=src. Byte identity is established on the tested environment, not all platforms. Input/config/code/model/file hashes and truthful generation-time dirty Git snapshots are retained. The later Git publication does not replace earlier provenance. Local passing tests are not a claim of observed GitHub CI success.

Raw data, row-level outputs, models, environments and private absolute-path manifests remain excluded from the portable review inventory/Git. Step 10 rejects package traversal, sensitive file types/paths, symlinks, excess size, credential patterns and machine-home paths; this bounded scan is not a legal/privacy certification. Exceptions fail closed, critical quality gaps block readiness without averaging and human checklist items remain unchecked. No upload/final-entry selection, organiser contact, Part 2 run, commit/push or publication is performed in Step 10. See docs/part1/reproducibility.md and reports/step10/final-readiness.md.

## Historical Step 1 scaffold description

The original stage-specific controls below remain as history; their limited component list and then-unpublished Git state are not the current repository state.

## Implemented components

- `doctor`: presence-only check for eleven local inputs.
- `inventory`: read-only Parquet schema, metadata, hash, required-field and key-coverage evidence; machine output is ignored.
- `iaa_hackathon.metrics`: fixed Tweedie power 1.5 with explicit weight and undefined-case handling.
- `iaa_hackathon.submission`: structural frame/CSV validation against exact sample IDs, with separate official-zero and local-strict-positive policies.
- `make step1-check`: raw-data-free schema, example and nonzero behavioral-test gate.

## Environment and controls

The exact tested Python 3.12 dependency versions are in `requirements/step1-py312.lock`; the recorded verification platform is macOS 26.6.2 x86_64. Platform-specific wheels may differ. CI is defined with read-only repository permission and synthetic tests, but GitHub execution has not been observed because no commit or push was requested.

Raw inputs, archives, local environments and generated row-level outputs are excluded from Git. The utilities do not train models, publish, submit or contact organisers. Exceptions fail explicitly. Human actuarial acceptance remains pending and is not replaced by automated or AI review.
