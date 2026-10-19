# Part 1 — decision summary for human review

## Task, selected approach and central limitation

The intended competition quantity is **expected net ultimate claim cost per 2025 policy-period row, in fictional currency units (CU)**, not charged premium or an unscaled annual rate. The actual frozen file predicts the separately identified **repaired observed-incurred snapshot proxy**. Claims are valued at 31 December 2024; monetary IBNR, further development, future recoveries and 2025 trend have not been established. This gap prevents an unqualified claim of defensible ultimate pricing or upload readiness.

The selected model is `S6_selected_compact_tweedie_glm`, one log-link power-1.5 GLM per line. Step 7's bounded LightGBM worsened the primary comparison; Step 8's additional contents curvature failed its preregistered materiality/uncertainty gate. The simpler S6 design was retained and refitted unchanged on all 2021–2024 repaired rows. No blend, additional feature, recalibration or leaderboard feedback was used.

| Evidence | Main 2023 fold | Reused 2024 challenge |
| --- | ---: | ---: |
| Selected S6 mean deviance | 103.496088 | 99.439308 |
| Selected S6 D², provisional pooled/unweighted | 0.113452 | 0.089801 |
| Observed-reference / predicted total (A/E) | 1.049931 | 0.908890 |
| Scored rows | 626,355 | 626,190 |

These are retrospective snapshot-proxy results, not observed-ultimate validation. Exact folds, response IDs, baselines and rejected experiments are in [results-and-diagnostics.md](results-and-diagnostics.md).

## Corrections and final local file

Reversible preparation repaired 123,664 motor customer references and 14,229 training exposures, exposed 3,527 inferred home sum-insured unit repairs, removed 604 exact duplicate-claim copies and quarantined 413 unmatched claims. Raw values were retained and raw input hashes are unchanged. The repaired observed response reconciles to 741,156,868.43 CU. Human adoption of repair/financial conventions remains pending.

The frozen CSV contains exactly 626,639 unique sample-order IDs and positive policy-period predictions totalling **189,554,001.45592618 CU**. One exposure multiplication, saved-model reloads and an isolated clean rebuild reproduce the file and model/schema bytes exactly in the pinned environment. Filename:

`submissions/part1_S6_glm_repaired_observed_net_incurred_snapshot_2024-12-31_873a17e390ff319b.csv`

SHA-256: `dfb3e565d97f0a4a597ab3051b6cffd616da5022aaf8da10aa0736db436e6274`.

## Readiness and authority

Mechanical correctness is not analytic approval. Current official pages could not be retrieved; deadlines, deliverables/Part 1 timing and entry limits are unresolved. Actual human actuarial challenge/sign-off is absent. The Step 10 [quality matrix](../../reports/step10/quality-bar-matrix.md) and [final-readiness report](../../reports/step10/final-readiness.md) must retain these critical gaps. A final paginated five-page report and a timed live-demo video are not produced by this Markdown set.

Next: resolve rules and target/basis judgement, then review the selected model and total using the [unchecked checklist](human-review-checklist.md). Any methodological change returns to the relevant earlier step and requires a new Step 9 candidate. No upload, final-entry selection, commit/push or Part 2 execution is authorised in Step 10.
