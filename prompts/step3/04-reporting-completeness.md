# S3-04 — Estimate reporting completeness, with truncation

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

Objective: implement a small, auditable reporting-delay/count-completeness estimator.

1. Declare the report population, cutoff, peril groups and exclusions. Start with
   simple pooled/peril-aware models and at most two suitable delay families;
   no neural networks or broad tuning. Do not pool BI with glass simply for
   convenience. Diagnose sparse groups, instability and calendar/cohort changes.
2. For claim j, D_j = report_date-loss_date and A_j = cutoff-loss_date. Fit an
   appropriate right-truncated likelihood conditional on D_j <= A_j. In a
   suitable model this contributes log f(D_j) - log F(A_j). Handle integer days,
   same-day reporting and boundary probabilities correctly. A naive censored
   survival fit is not automatically a valid truncated-data estimator.
3. Produce F_k(a), count-completeness estimates and fit metadata. Document tail
   assumptions beyond observed support; a fitted tail is not observed truth.
   Inspect convergence, monotonicity and probabilities in [0,1]. Do not silently
   floor tiny F values or cap enormous inverse weights. Flag weakly supported
   cohorts and provide an explicit sensitivity or mature-cohort alternative.
4. For a row/peril, compute average count-reporting completeness over covered
   loss dates using the declared occurrence-time assumption. Uniform daily
   incidence is a working assumption, not a fact; examine seasonality/mix.
   Prefix sums/lookup tables can avoid millions of Python day-by-day loops.
   Record effective reported exposure = clean exposure * completeness for a
   later count model, respecting verified peril eligibility. Do not multiply
   an already observed monetary target by exposure again.
5. Backtest counts at earlier cutoffs, e.g. end-2022/end-2023: fit only claims
   reported by the cutoff, then compare predicted reports over the available
   follow-up window with reports actually seen by end-2024. Do not label the
   final available count ultimate, or use final monetary/status fields as though
   known at the earlier cutoff. These are finite-follow-up count checks.
6. Test a synthetic known delay mechanism under truncation, complete reporting,
   same-day claims, sparse groups, unstable tails and cutoff leakage. Explicit
   fit/report cutoffs and reusable fit/transform functions are required.

Acceptance: count-completeness estimation is diagnosable and backtested within
available follow-up. This does not yet establish amount completeness or case
adequacy. If estimation is unstable, preserve that result instead of inventing
a production factor. Next: S3-05.
