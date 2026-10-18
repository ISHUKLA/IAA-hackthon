# S3-05 — Specify reported-claim and recovery scenarios

## Common instructions

Execute only this prompt. Read the current AGENTS.md, the Step 1 contract,
Step 2 manifest/config and relevant evidence. Keep raw data and prior clean
outputs immutable. Use the existing Python 3.12 environment and utilities;
add only required dependencies and retain an exact tested lock.

All claim-level, policy-level target, exception and scenario outputs belong
under ignored outputs/step3/. Commit only code, configuration, genuinely
synthetic fixtures and reviewed aggregate documentation. Preserve row identity.

Separate measured facts, estimates, explicit assumptions and pending decisions.
Do not fabricate future payments, historical financial snapshots, unreported
claim records, actuarial approval or validation results. Perform ordinary
reversible work without repeated permission requests; ask only for a genuinely
missing decision required to adopt a final assumption. Continue useful work
that does not depend on that decision.

Do not train pricing models, create validation splits or test targets, tune
to a public leaderboard, generate competition predictions, commit or push.
Use synthetic tests for behavioral contracts and actual-data reconciliations
for data acceptance. Report them separately. Do not spawn subagents.

Finish with changed files, actual commands/results, reconciliations, remaining
limitations and the next prompt. Update status and PROMPT_LOGS.md truthfully.
Never turn AI review or machine tests into human approval. Do not automatically
run the next prompt.

## Prompt-specific instructions

Objective: implement a transparent scenario engine for quantities not identified
by the single financial snapshot. Do not claim estimated factors without evidence.

1. Define documented parameters by credible line/peril groups: treatment of
   outstanding case reserves and future recoveries. A reference case multiplier
   of one and zero additional recovery reproduce current case assumptions;
   they are neutral references, not proof of adequacy. Low/high values need
   evidence or must be labelled illustrative stresses, not confidence bounds.
2. Where P=paid and I=incurred share the same net-of-excess, gross-of-recoveries
   basis, case reserve C=I-P. A reported net-ultimate candidate can be written
   P + a*C - R_observed - R_future. Equivalently, adjust observed net incurred
   by (a-1)*C and subtract future recovery once. Apply a to the case reserve,
   not paid amounts or the entire incurred balance. Adapt if field meanings differ.
3. Allow reserve release as well as strengthening: do not force a >= 1 just
   because a claim is open. Do not infer a 1.2–1.3 BI factor from a severity
   ratio confounded by mix, reporting selection and extreme losses.
4. Examine recovery evidence separately for own_damage/theft. Observed closed-
   claim recovery ratios can inform a sensitivity but are selected samples;
   current zero recovery on open claims is not a final recovery forecast.
   Avoid subtracting observed recoveries twice. Document assumptions for future
   recovery on reported claims and net severity for unreported claims separately.
5. Test identity/reference behavior, reserve strengthening/release, closed claims
   with no case reserve, no double recovery/excess subtraction and invalid
   parameter/negative-net exceptions. Never silently clip an invalid scenario.
6. Quantify scenario impacts and contributions of the largest BI claim. Preserve
   source amounts. Keep trend/inflation separate and disabled here unless the
   user explicitly specified its treatment; do not stack arbitrary uplifts.

Acceptance: observed amounts, signed case adjustment and future recovery are
separate. Parameters and human review status are explicit. Missing actuarial
support stays a pending assumption, not a fabricated optimum. Next: S3-06.
