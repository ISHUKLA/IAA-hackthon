# Part 1 reproducibility and controlled handoff

## Prerequisites

Use Python 3.12.11 and `requirements/step7-py312.lock` (26 exact packages), on the recorded macOS x86_64 platform for the tested byte-level guarantee. No new dependency is required by Step 10. The working package source is used explicitly through `PYTHONPATH=src`; the local wheel installation history is not a hidden import dependency.

The original eleven public inputs must be available in the caller's private directory, with hashes matching `configs/final_model.json`. Repaired/frozen Steps 2–9 artifacts must also be available under the recorded relative `outputs/` paths. These include the repaired policy/claim/audit layer, recovered folds and repaired response/reporting views, prior experiment evidence and the frozen benchmark/decision/acceptance. S9's immutable preflight checks those registered upstream identities, including prior challenger artifacts. The public Git clone alone intentionally lacks these private row/model artifacts. This is reproduction from controlled repaired sources/evidence, NOT a claim that a public clone contains competition data or a self-contained numerical bundle.

Arrange any necessary private local transfer separately with authority. Do not upload raw data or strip required frozen evidence and then assert the same preflight passed. Existing earlier commands can rebuild preparation/experiments when separately authorised; Step 10 does not rerun model selection or change their registries.

## Commands

From repository root, provide the actual existing official-data directory as `DATA_DIR`. It is not hard-coded or copied into the review package:

```sh
make step10-check PYTHON=.venv/bin/python
make step10-freeze PYTHON=.venv/bin/python
make verify-submission PYTHON=.venv/bin/python DATA_DIR='/path/to/official/public'
make reproduce-part1 PYTHON=.venv/bin/python DATA_DIR='/path/to/official/public'
make step10-review PYTHON=.venv/bin/python DATA_DIR='/path/to/official/public'
make verify-part1-package step10-acceptance PYTHON=.venv/bin/python DATA_DIR='/path/to/official/public'
```

The Step 9 verification command rereads the existing candidate and checks exact sample IDs/order, raw test reconciliation, finite positive period predictions and reload equivalence. It must not create a missing final candidate. `reproduce-part1` uses a fresh empty artifact directory plus numerical-code snapshot, reads the repaired layer again, fits only the exact frozen three GLMs and compares CSV/model/schema bytes. Original CSV hash, size and modification time plus all frozen model/config/code/manifest hashes are checked before/after. It does not reuse fitted production models or overwrite the frozen candidate.

`step10-review` adds post-selection aggregate regional A/E and repaired BI/subsidence maturity/case summaries without changing any model/response. `verify-part1-package` verifies the candidate and creates the local inventory/manifest/readiness record; `step10-acceptance` checks payload hashes, evidence completeness and faithful blocker/unchecked-human statuses. A passing package acceptance can correctly coexist with `blocked` upload readiness. Actual commands, counts and timings are recorded under `outputs/step10/`, not assumed from Make-target existence.

## Provenance

The original Step 9 manifest retains its truthful pre-commit dirty snapshot. The later published Git commit `fd4ab36a5c47d4a9c164fe8751414eb8a1a66313` contains the same numerical code; publishing did not backdate a clean identity into the old manifest. Some documentation was subsequently clarified; current document hashes are recorded by Step 10 separately. Private historical absolute-path metadata remain outside the portable review inventory rather than being rewritten. Numerical generation provenance and current narrative provenance are distinct.

Step 10 inventory paths are repository-relative, with text/secret/home-path/symlink/size checks. It includes code, configs, tests, prompts, aggregate reports/cards/logs and selected aggregate verification artifacts, not raw data, row CSV/Parquet, fitted objects, caches/environments, credentials, archives or discarded fitted searches. The frozen candidate and models are referenced separately in the local controlled workspace. No archive is created because no verified current official instruction or existing workflow requires one. Every generated manifest version is retained by content hash under `outputs/step10/package-records/`.

The recorded clean rebuild is byte-for-byte exact in the tested environment; cross-platform equivalence is not promised. PyArrow sandbox cache-sysctl warnings and Joblib physical-core fallback are nonfatal and disclosed, not silently counted as successful tests. Full GitHub CI execution has not been inspected; local tests are not an independent CI result. If payload docs change, rerun package verification/acceptance to obtain a new package hash; never alter the frozen candidate for presentation.
