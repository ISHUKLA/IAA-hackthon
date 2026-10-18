# Prompt 04 — Implement and verify the metric contract

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Implement a small scoring utility using the documented standard implementation. Do not train a model or infer the competition's unknown weighting.

## Procedure
1. Read the contract and official sklearn documentation. Add src/iaa_hackathon/metrics.py with fixed-power-1.5 mean Tweedie deviance and D², plus explicit optional sample weights. Name the provisional pooling/weighting choice in reports.
2. Validate lengths, finite inputs, nonnegative targets, strictly positive predictions and valid weights. Do not silently floor values, change the power, swap y_true/y_pred or annualize row targets.
3. Specify and test the policy for all-zero/constant targets, zero total weight and too few rows. An undefined D² must be reported as undefined or raised clearly, never converted to a fabricated success score. Mean deviance can still be useful.
4. Add meaningful synthetic tests: empirical-mean null gives D² zero on nonconstant targets; perfect predictions on positive, nonconstant targets give one; a deliberately poor predictor is worse; invalid predictions are rejected; optional weighting is correct.
5. Use an independent arithmetic check: for p=1.5, deviance(y, mu)=4*(y/sqrt(mu)+sqrt(mu)-2*sqrt(y)). For y=[0,4] and mu=[1,1], mean deviance is 4. Compare this hand result with the utility. Do not merely test one wrapper against itself.
6. Demonstrate row-loss/rate equivalence if used: scaling both y and mu by exposure scales deviance by exposure^(2-p). For unweighted row loss at p=1.5, equivalent rate scoring uses sqrt(exposure) weights. Standard exposure-weighted rate fitting is a different objective. This is conditional on the scoring contract, not a new official fact.
7. Install only needed Step 1/dev dependencies. Record exact versions and the Python/platform context in a lock; exclude editable local absolute paths. Verify reinstallability in a fresh environment before claiming reproducibility. Update CI to run the actual metric tests.

## Acceptance
Independent arithmetic and behavioral tests pass. Undefined cases and provisional competition semantics are explicit. No real-data validation score is invented. Next: Prompt 05.
