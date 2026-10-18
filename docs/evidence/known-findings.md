# Previous direct-audit findings — reverify against the local files

These are aggregates from the uploaded data, not organiser guarantees. The companion expected-manifest.json contains file metadata and hashes. A changed hash invalidates any automatic assumption that the earlier audit applies unchanged.

| Finding | Evidence/status | Consequence for Step 1 |
| --- | --- | --- |
| Training/test split | Training 2021–2024; test 2025; 626,639 test rows | Define the prediction horizon; do not resplit the competition test |
| No ultimate labels | Single financial valuation at 31 December 2024 | An incurred reference is not ground-truth ultimate |
| Motor customer IDs | Padding to 8 characters resolves 98,110 train and 25,554 test joins | Document a later cleaning requirement |
| Exposure errors | 14,229 train rows; day/360 patterns inflate totals 34–37% | Specify inclusive ACT/365; preserve raw values later |
| Sum insured | 2,797 train and 730 test home values form a likely x1,000 cluster | Strong unit-error interpretation, not confirmed truth |
| Claim linkage | 162,736 exact single matches; 414 before first supplied coverage; zero multiple matches | Define coverage by loss date; quarantine exceptions later |
| Recoveries | 27.68 million CU; 22.48% of motor own-damage incurred | Explicit net-cost basis and future-recovery uncertainty |
| Long-tail maturity | 2024 open shares: BI 79.8%, subsidence 68.7% | Distinguish IBNR from reported-claim development |
| Large loss | Motor BI incurred 11.89 million CU | Do not silently delete or call it noise |
| Suspect contacts | Near-deterministic association with observed claims | Timestamp unresolved; quarantine core use |
| Renewals | About 84.8% of test policies seen in training | Chronological validation with returning-risk diagnostics |
| Weather | All test addresses have 2025 weather | Availability at prospective pricing is unresolved |

Selected ordinary predictors have about 2.5–3% missingness; non-opt-in telematics-score absence is structural. Observed net-cost zeros are about 90.0% motor, 96.4% buildings, 96.8% contents. Sample predictions are all zero placeholders.

Step 1 records definitions and risks. It does not perform these corrections, estimate ultimate losses or implement model training.
