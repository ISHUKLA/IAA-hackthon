# Step 1 acceptance and handoff

## Acceptance status

Machine verification is complete on the recorded local Python 3.12 platform. Human actuarial acceptance remains **pending**. Step 1 defines and tests the contract; it does not establish actual ultimate labels, model performance or competition acceptance.

| Objective | Contract position | Evidence |
| --- | --- | --- |
| Prediction grain | One `row_id` covered policy-period row; line comes from claims plus policy-table identity; inclusive loss-date allocation | `configs/problem_contract.json`; schema and contract tests; `docs/step1/problem-definition.md` |
| Net financial basis | Expected total ultimate cost net of excess and recoveries; never double subtract excess | Target contract and A03; unresolved source-field interpretation remains `null` |
| Ultimate versus observed reference | Observed net incurred, unreported loss, reported development, future recovery and trend are separate; no actual ultimate label supplied | Target contract; problem definition; challenge review |
| Exposure | Row-period cost; apply exposure once; inclusive ACT/365 is a proposed later reversible correction | Exposure contract; 50 CU example; A15; no correction executed |
| Fixed metric | Standard mean Tweedie deviance and D² at power 1.5, explicit optional weights and undefined cases | `src/iaa_hackathon/metrics.py`; independent arithmetic and behavioral tests |
| Submission identity | Exactly `row_id,prediction`, 626,639 exact test IDs, finite numeric values and official minimum zero; strict positivity separate | Submission contract/checker; synthetic CSV reread tests; real sample coverage inventory |
| Assumptions | Pooling/weights, financial interpretation, maturity, recovery, feature timing, order and related choices remain explicit | `docs/assumptions.md`; unresolved JSON values; challenge dispositions |
| Review state | Automated contract checks pass and AI challenge is complete; neither is human approval | Contract approval object; `docs/step1/challenge-review.md`; status/log |

## Verification boundary

`make step1-check` validates required Step 1 files, the JSON/schema, the required arithmetic examples, nonzero test collection and all contract/metric/submission synthetic tests. The final run collected and passed 45 tests. It needs no raw data. Local-data inventory is a separate command and was already evidenced in Prompt 02.

The exact 25-distribution lock and local package were reinstalled in a fresh Python 3.12.11 environment. The fresh `make step1-check` passed all 45 tests and `pip check` reported no broken requirements. This verifies the recorded platform and package set; it does not promise identical wheels or numerical behavior on every operating system or architecture. CI uses the same exact version lock and commands, but its GitHub result remains unobserved until a future push.

## Human decisions still needed

- Competition score pooling, weighting and scorer implementation.
- Supplied incurred/paid/excess/recovery accounting and future-recovery treatment.
- Inclusive ACT/365 correction approval and reconciliation.
- Unreported-loss, reported-development and 2025 trend assumptions.
- Unmatched claim treatment and declined/repudiated terminology.
- As-of availability of contact, historic financial, customer and weather features.
- Strict-positive operational policy and whether order has an official requirement.
- Validation use of immature 2024 outcomes, model architecture and final report layout.

## Later work, outside Step 1

Actual reversible cleaning; claim linkage and financial reconciliation; maturity and recovery modelling; target scenarios; chronological split manifests; safe feature construction; baselines; predictive training and comparisons; real prediction generation; final file hashing; human selection; and any authorised upload.
