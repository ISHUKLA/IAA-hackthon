# Part 1 results and diagnostics

All scores below use `repaired_observed_net_incurred_snapshot_2024-12-31`, exact frozen memberships, power 1.5 and provisional pooled unweighted period-cost scoring. F2023 has 626,355 rows; F2024 has 626,190. Across-year D² denominators differ; model comparisons are within the same fold/response.

| Model / decision | F2023 mean deviance | F2023 D² | F2024 mean deviance | F2024 D² |
| --- | ---: | ---: | ---: | ---: |
| B0 training mean | 116.741540 | -0.000009 | 109.506007 | -0.002342 |
| B1 line exposure rate | 106.616810 | 0.086719 | 101.500296 | 0.070937 |
| B2 conditional premium comparator | 107.938563 | 0.075397 | 102.264710 | 0.063940 |
| B3 compact GLM | 104.041285 | 0.108781 | 99.947988 | 0.085145 |
| S6 selected features — retained | 103.496088 | 0.113452 | 99.439308 | 0.089801 |
| S7 LightGBM — not promoted | 104.122711 | 0.108084 | 98.856180 | 0.095139 |
| S8 one contents coefficient — not promoted | 103.494465 | 0.113465 | 99.439751 | 0.089797 |

Sources: `docs/step5/baseline-results.md`, `docs/step6/feature-results.md`, `docs/step7/lightgbm-results.md`, `reports/step8/candidate-comparison.md` and their hashed manifests. S8's primary gain 0.001623 was below 0.060401, with interval [-0.003475, 0.007130]. The tiny gain did not earn complexity. S7's favourable reused challenge did not override its worse primary comparison/calibration.

## Calibration, segments and tails

Selected pooled A/E is 1.049931 in F2023 and 0.908890 in F2024. F2024 motor A/E is 0.803431; returning-policy A/E is 0.897049 versus 1.021134 for new policies. This is material maturity/calibration uncertainty, not grounds for a forced portfolio adjustment.

Step 10's guarded one-to-one prediction join and many-to-one address join add regional review on unchanged saved predictions. Twelve regions per line reconcile to every held-out row (72 line/fold/region groups):

| Line | F2023 regional A/E range | F2024 regional A/E range |
| --- | ---: | ---: |
| Motor | 0.6703–1.5704 | 0.6346–0.9761 |
| Buildings | 0.8468–1.2102 | 0.5947–1.2419 |
| Contents | 0.7440–1.5848 | 0.7009–1.3892 |

These are post-selection descriptive ranges, not calibrated segment guarantees or independent confidence intervals. They show why aggregate totals alone are insufficient. All regional rows/exposures/observed/predicted totals and scores are in `outputs/step10/aggregate-review.json#region_calibration`; no regional recalibration or feature was added.

The 11,894,276.93 CU BI claim remains in primary scoring. Subtracting only its amount from the fixed primary-fold response changes S6 mean deviance from 103.496088 to 101.088331; predictions and rows stay fixed. This sensitivity does not justify deleting the claim. Current repaired 2024 known-claim open shares are 940/1,178 (79.7963%) for BI and 200/291 (68.7285%) for subsidence. Their case balances are 14,111,478.94/4,479,108.99 CU; ±20% reference stresses are ±2,822,295.788/895,821.798 CU, not identified ultimate allowances.

## Frozen 2025 file — not a test-set score

| Line | Rows | Predicted period cost CU |
| --- | ---: | ---: |
| Motor | 254,986 | 106,408,103.14559814 |
| Buildings | 184,155 | 65,758,748.39939484 |
| Contents | 187,498 | 17,387,149.91093321 |
| Total | 626,639 | 189,554,001.45592618 |

Clean exposure is 500,351.282; cost/exposure is 378.84184227 CU. There are 795 predictions below 1 CU (maximum associated exposure 0.0219), none above 10,000 CU. All are finite and positive, with exact sample order and saved-model equivalence. Same-2025-row full refitting changes motor/buildings/contents totals by -5.4755%/+1.2164%/+1.0220% versus F2024 fold models. No totals were forced.

S9 production/reproduction took 32.09/44.28 seconds; Step 10's independent fresh refit/rebuild took 58.23 seconds, with identical CSV/model/schema bytes and the original file untouched. These whole-command timings are not controlled model speed comparisons. No 2025 labels, score, leaderboard result or ultimate calibration is available. Full quantiles, return segments and financial/SI sensitivities remain in `reports/step9/submission-diagnostics.md` and its hashed aggregate JSON.
