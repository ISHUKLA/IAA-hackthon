# Part 2 handoff — plan only; not executed

Part 2 has not been executed. Its schema, target, financial basis, market features and outcome behavior are unknown. This handoff demonstrates reusable controls, not predicted adaptation success or permission to start processing new data.

## Frozen Part 1 identifiers

| Component | Frozen reference |
| --- | --- |
| Original inputs | Eleven hashes in configs/final_model.json#raw_sha256; reference manifest docs/evidence/expected-manifest.json |
| Repaired training/test | outputs/step2/repairs/model/training-model-table.parquet / test-model-table.parquet; SHA-256 26fe66401b44aff157754c9166c8117b8345c6e94c1d88a6a87bc8dda986d793 / 82a6a968f1c16b10c97c9657c4c20098082a920bc6758e4a6413148269a5a60b |
| Claim universe | matched.parquet SHA-256 994815e1c39e4b37bd55a8a12e0cf4e9b65d542052fed075a8f855841f55cd85; repair audit e0b5cb5265cc6888ddea243b804f356f630cefb964f5c3947247bc02939e4433 |
| Schemas | Logical JSON contracts under schemas/ plus actual repaired training/test/claim Arrow schema identities in outputs/step10/aggregate-review.json#schema_identifiers |
| Features | configs/features.json SHA-256 7062e45171c609b323f94740b508ee9beb5963a5c695e2f63a16d87757490c18; exact final allowlist/blocks in configs/final_model.json |
| Response | repaired_observed_net_incurred_snapshot_2024-12-31; incurred less recorded recoveries, identity case/development/recovery/trend proxy, NOT ultimate |
| Folds | F2023 primary/F2024 reused challenge; logical membership f444d8c7f7a91e842a5f2789d212121bb65578d4e1389ce5cf56f3f4eb1a7fa5; readable-file SHA-256 2f7cf05e0b41cc92466d7cff4f560b49157dba8b8979c7e355676baa07ca0eaf |
| Model/config | S6_selected_compact_tweedie_glm; step9-frozen-S6-observed-proxy-v2-immutable-audit; config SHA-256 873a17e390ff319bf14c645703065e04cb38fae33733f901ff28be0251ed408b |
| Fitted objects | outputs/step9/models/{motor,buildings,contents}.joblib plus schemas; exact hashes in outputs/step10/frozen-candidate.json and original Step 9 manifest |
| Environment/code | Python 3.12.11, 26-package requirements/step7-py312.lock; frozen numerical-code hashes in configs/final_model.json; Step 10 current Git/patch/inventory recorded separately |
| Submission | 626,639 rows, 189,554,001.45592618 CU; filename ending _873a17e390ff319b.csv; SHA-256 dfb3e565d97f0a4a597ab3051b6cffd616da5022aaf8da10aa0736db436e6274 |

## Reuse controls, not Part 1 assumptions

Reusable: immutable inventories, schema/value contracts, safe joins, raw-versus-derived ledgers, claim coverage reconciliation, metric-domain tests, fold-local processing, feature allowlists, saved-model reloads, paired comparisons, uncertainty/segment/tail summaries, audit provenance and exact submission checks. They require parameterisation/review for the new task.

Part 1-specific: eight-character motor padding; ACT/365/rounding; x1000 SI inference; exact duplicate criteria; status meanings and recovery basis; peril/reporting-delay family; 2024 snapshot; feature names/categories; fold years; loss scale/exposure; fitted medians/vocabularies/coefficients; row prefixes/counts/sample order and the current proxy response. **Do not blindly apply Part 1 corrections, financial assumptions or fitted models to Part 2.**

## Required schema/distribution comparison and tests

| Area | Compare and fail/review condition |
| --- | --- |
| Files/columns/types | Hash raw files first; list missing/new/renamed columns, precision/date/timezone changes and schema incompatibilities. Missing required fields fail closed; do not silently coerce |
| IDs and row grain | Establish row/entity keys and policy-period unit anew; test null/duplicate keys, canonical-width collisions and zero join multiplication; no numeric ID coercion |
| Categories/missingness | Measure new/lost categories and line/year-specific missingness; separate structural from ordinary absence; unknown-category behavior and imputation fit only on permitted training |
| Units/exposure/dates | Reconcile currency and SI scale, stored days/annual fractions, denominator/leap dates, inclusivity, period overlaps/cancellations and year ranges. Test exposure once at train/predict/reload |
| Claims/status/basis | Verify actual loss/report/payment fields, accepted/declined labels, duplicates and quarantine, financial precision, recoveries/excess; row/count/money reconciliation before targets |
| Reporting/maturity | Establish valuation vintages and truncation; compare lag/open/case/severity/recovery patterns by peril/cohort. Counts do not automatically imply monetary completeness |
| Target/availability | Establish expected ultimate versus observed reference, net basis, evaluation definition and feature timing. Perturb held-out outcomes and assert preprocessing/predictions unchanged |
| Validation/drift | Select task-appropriate chronological/geographic/other challenge splits before modelling; compare risk mix, exposure, claim rates, segments and credible uncertainty, not pooled score alone |
| Model/file boundary | New training-only baselines first; same-row response versions, convergence, saved reloads; exact new sample coverage/order/domain/count and cost units. Do not carry over 626,639 or M/B/C by assumption |

The checklist is not a claim that drift tooling was run on unseen Part 2 data. Do not infer that a feature's apparent Part 1 usefulness or governance status transfers across markets.

## Prioritised adaptation order and success evidence

1. New data contract: verified raw identities/schemas, reversible repairs, joins and financial reconciliation.
2. New response contract: explicit ultimate/observed components, timing, assumptions and real human review.
3. Validation: freeze appropriate populations, response versions, cutoffs and scorer semantics.
4. Baselines: exposure-aware transparent references and compact models on the new task.
5. Features: prospective availability, train-only transforms and fixed-comparison ablations.
6. Challenger: bounded new-market comparison only if residual evidence and budget justify it; no automatic complex-model transfer.
7. Submission: freeze selected design, refit/reload, new sample join, exact-domain/coverage/units/financial gates, independent reproduction and separate human upload/final-selection decisions.

Minimum evidence before claiming adaptation success: actual Part 2 inventory/profile diffs and resolved contracts, all new raw/row/money/availability tests, predeclared validation with appropriate target limitations, baseline and challenger results on exact comparable rows, calibration/segment/tail/drift findings with uncertainty, documented changed/rejected assumptions and genuine human decisions, and a reproducible correctly formatted local file. Part 1 performance or this checklist alone is insufficient. Starting any of this requires a separate user instruction.
