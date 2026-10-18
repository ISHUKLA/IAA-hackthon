# Step 2 acceptance and Step 3 handoff

## Automated acceptance

- `make step2-check` collects and passes a nonzero raw-data-free synthetic suite covering deterministic repairs, error paths, joins, atomic publication, source preservation and reruns.
- `make step1-check` remains the independent Step 1 regression gate.
- `make prepare-data` rebuilds all six policy tables from raw inputs plus the versioned cleaning configuration.
- `make step2-acceptance` checks all 3,035,950 policy rows, exact identity/order, reference counts, complete dimension linkage, expected correction/candidate counts, unchanged test exposure, unchanged premium totals, unchanged raw hashes, rerun digest equality and absence of tracked Step 2 row data.
- CI defines a separate raw-data-free Step 2 job using `requirements/step2-py312.lock`. Its presence is not evidence that GitHub Actions ran.
- The local Python 3.12.11 environment matched all 25 exact lock entries, the current package wheel installed with local build isolation disabled after the lock was present, and `pip check` reported no broken requirements.

## Skeptical challenge result

The checks reject malformed/unresolved IDs, dimension collisions, invalid or unexplained dates/exposure, cross-year weather selection, row multiplication, original-column mutation, raw-hash changes and partial publication. Leading-zero IDs are never converted through numbers. Leap-day and 366-day periods are explicit. Sum-insured candidates derive only from the preserved raw field, remain labelled inferred and cannot be double-divided. Structural telematics missingness stays missing, while a below-14 licensing-age result is only a flag. Claims, targets, outcome-based transforms and model features are absent from the preparation code.

## Human review and handoff

Automated/AI checks are complete for Step 2; human actuarial review remains pending. In particular, a human must decide whether to adopt the ACT/365 exposure convention and the factor-of-1,000 sum-insured candidates downstream. Weather availability and all customer/history aggregates require prospective/as-of timing evidence.

Step 3 may consume the six clean policy tables and immutable raw dimension/claim references using the recorded manifest. It must retain the raw/derived distinction and must independently address loss-date claim linkage, unmatched claims, financial-field meaning, development/IBNR and validation design. Step 3 was not started here.
