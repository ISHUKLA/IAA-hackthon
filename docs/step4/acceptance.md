# Step 4 acceptance status

Synthetic framework checks cover calendar membership and strict supplied-prediction alignment. Real-data folds were published under ignored `outputs/step4/folds/` from the repaired policy universe. The repaired observed response remains a retrospective snapshot proxy.

The prerequisite gap was closed before S5: `outputs/step4/repaired-views/` contains row-aligned responses and 15 repaired-universe reporting fits for each fold, with policy, claim, repair-audit and artifact hashes. Raw-claim Step 3 scenarios remain incompatible and are blocked; therefore no scenario sensitivity is claimed. The observed-response validation framework is ready for S5 as a retrospective snapshot proxy, not ultimate truth.

Step 7 recovery, 19 October 2026: after the earlier Step 8 preflight detected Snappy/Parquet corruption, the saved membership was reconstructed from the same repaired policy table and validation configuration. Its logical digest exactly matched the existing frozen summary (`f444d8c7f7a91e842a5f2789d212121bb65578d4e1389ce5cf56f3f4eb1a7fa5`). Original bytes and their SHA-256 were preserved under ignored `outputs/step7/fold-recovery/` before replacement. S6 saved-model and exact held-out coverage checks passed against the recovered folds. This repairs an artifact, not a split definition or response; see `docs/step7/acceptance.md`.
