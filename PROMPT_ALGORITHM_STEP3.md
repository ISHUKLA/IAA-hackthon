# Step 3 prompt algorithm — claim targets and the maturity bridge

Prepared 18 October 2026 for ISHUKLA/IAA-hackthon. This is a prompt guide for execution in the existing local checkout. No target construction, reserving model or cleaning execution is claimed by this document.

## Scope and prerequisites

Step 3 converts the clean training policy rows and claim snapshot into (1) a reconciled observed response, (2) reporting/maturity diagnostics and estimators, and (3) explicitly conditional development candidates. It cannot recover unobserved true ultimate losses from a single financial valuation.

The valuation date is 31 December 2024. Work on training periods in 2021–2024. Do not construct claim targets for the 2025 test rows or treat sample zeros as labels.

At inspection, GitHub contained the implemented Step 1 contract and tests, but configs/cleaning.json and docs/step2/acceptance.md were not visible on main. Step 2 work may exist locally and its data outputs are intentionally ignored. S3-00 must inspect the actual local state. Absence on GitHub alone neither proves nor disproves completion.

Preserve the existing checkout, source files, Step 1/2 behavior, origin and unrelated edits. Do not import the original scaffold over current work. This request advances the active scope to Step 3, while retaining historical phase records and pending human approvals.

Pricing GLMs/GBMs, premium prediction, validation split generation, tuning and submission remain later work. A small reporting-delay estimator is reserving work explicitly within this stage; it is not authorisation for a pricing-model search.

## Bootstrap — avoid referring to files before creating them

Save this guide in Downloads or attach it to the harness. Paste:

```text
Work in the existing ISHUKLA/IAA-hackthon checkout.

Read the supplied IAA_Step3_Prompt_Algorithm.md; if it is not attached,
read ~/Downloads/IAA_Step3_Prompt_Algorithm.md.

Read AGENTS.md and current local status. Preserve implemented Step 1/2
work and the existing Git repository. Do not assume Step 2 is complete
merely because Step 1 passed, or incomplete merely because it was not pushed.

Copy the guide to PROMPT_ALGORITHM_STEP3.md. Create prompts/step3/ and
write S3-00 through S3-07 below to their stated filenames, including
the Common instructions in every file. Compare rather than overwrite
any existing Step 3 work.

Update only the active-scope paragraph in AGENTS.md to permit requested
Step 3 claim linkage, reconciliation and reserving diagnostics. Preserve
the restrictions on pricing-model training, later steps, publishing and
fabricated human approval.

Execute ONLY S3-00. Report files changed, actual check results, prerequisites,
unresolved assumptions and the next prompt. Do not commit or push.
```

Continue one prompt per turn, reviewing its evidence before the next. Example: `Read AGENTS.md. Execute only prompts/step3/01-claim-linkage.md.`

## Common instructions

Include these instructions in every numbered prompt:

```text
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
```

## Reference measurements — conditional on unchanged input hashes and basis

These are prior audit results to reverify, not constants for a function to return. The observed-cost reference below uses matched, non-repudiated incurred less recorded recoveries. Its financial interpretation must be checked against field definitions.

| Check | Previous direct-audit result |
| --- | ---: |
| Source claims | 163,150 |
| Exactly one coverage match | 162,736 |
| Multiple coverage matches | 0 |
| No coverage match | 414; all before the first supplied period of their otherwise known policy |
| Unmatched loss years | 274 in 2020; 48 in 2021; 48 in 2022; 44 in 2023 |
| Unmatched incurred | 1,786,987.70 CU |
| Source incurred | 773,731,129.10 CU |
| Source recorded recoveries | 27,678,633.34 CU |
| Matched accepted recorded recoveries | 27,613,464.36 CU |
| Motor observed net-incurred reference | 430,595,512.14 CU |
| Buildings observed reference | 247,768,586.05 CU |
| Contents observed reference | 65,966,578.85 CU |
| Total observed reference | 744,330,677.04 CU |

The 1,711 repudiated source claims have zero observed paid, incurred and recoveries, but remain explicit exclusions. Do not derive claim counts from positive monetary cost: accepted zero-cost claims and multiple claims per policy-period are possible.

Long-tail priorities are motor bodily injury and buildings subsidence. The largest source claim is open motor bodily injury: incurred 11,894,276.93 CU and paid 738,769.47 CU. Preserve it in the primary reconciliation. Observed recoveries occur only on closed claims; this does not prove that open/unreported claims will never produce recoveries.

## S3-00 — Preflight and target-construction specification

Prompt file: `prompts/step3/00-preflight.md`

```text
Objective: establish valid local prerequisites and the exact target components.

1. Read AGENTS.md, context.md, what-good-looks-like.md, the latest source
   register, problem contract, Step 2 cleaning configuration, acceptance and
   output manifest. Inspect local Git state. Reconcile stale status statements.
2. Run the implemented Step 1 and Step 2 synthetic checks. Verify the full-data
   Step 2 manifest, source identities and clean row sets. Do not accept the mere
   presence of a report as proof. If local Step 2 outputs are absent, identify
   that exact prerequisite; prepare the Step 3 specification and source review
   without fabricating outputs or silently redoing all of Step 2.
3. Identify actual claims fields: claim_id, policy_id, line, peril, loss_date,
   report_date, status, paid_to_date, incurred_to_date and recoveries. Verify
   types, identifiers, statuses, report/loss chronology and the valuation cutoff.
4. Write configs/target_construction.json and docs/step3/target-plan.md. Specify
   coverage linkage, disjoint exception classes, financial basis, precision,
   reported-count definitions, component names and provenance/status fields.
   Resolve field meanings from official documentation where possible. If
   whether incurred already nets recoveries is ambiguous, show the competing
   interpretations; do not silently choose by which gives a nicer score.
5. Distinguish observed net incurred, reported-claim development, unreported net
   losses, future recoveries on reported claims and optional trend. Preserve
   the incurred-minus-observed-recoveries audit reference as provisional where
   necessary rather than falsely certifying its financial interpretation.
6. Define APIs with explicit fit populations and report/as-of cutoffs so later
   validation can refit estimators without using held-out outcomes. Full-snapshot
   estimates must be marked full-snapshot, not represented as fold-safe.

Acceptance: local prerequisite status and target schema are explicit; missing
inputs or source ambiguity remain visible. No ultimate labels are invented.
Next: S3-01.
```

## S3-01 — Link claims to loss-date coverage

Prompt file: `prompts/step3/01-claim-linkage.md`

```text
Objective: assign each eligible source claim to its correct training policy-period.

1. Validate claim_id uniqueness and policy-period non-overlap within line/policy.
   Match claims.line and policy_id to the correct policy table, then require
   period_start <= loss_date <= period_end. Mid-term rows must stay distinct.
2. Produce a claim-to-row crosswalk with match count and disposition. Partition
   source claims into exactly-one-match, unmatched and ambiguous/multiple-match
   groups. Never silently drop duplicates or choose the nearest row.
3. Classify unmatched cases: unknown line/policy, before first supplied coverage,
   after last coverage, between periods, invalid date, or other explicit cause.
   Quarantine exceptions with their original amounts and dates. Do not shift a
   loss date or attach the 414 known exceptions to an arbitrary renewal.
4. Reconcile counts and monetary totals across the disjoint linkage groups.
   For identical audited inputs expect 162,736 single matches, 414 pre-coverage
   exceptions and no multiple matches. Verify rather than hard-code.
5. Test boundary dates, a next-year report for an in-period loss, mid-term changes,
   gaps, wrong line, unknown policy, overlapping periods and repeated claim IDs.
   Allocate by loss date; report/payment dates do not select the coverage row.
6. Keep claim outcome fields in the response-construction area. Do not promote
   them into pricing features or join them onto future test rows.

Acceptance: every source claim has a traceable disposition and all counts and
amounts reconcile; ambiguous matches cannot pass silently. Next: S3-02.
```

## S3-02 — Construct and reconcile the observed response

Prompt file: `prompts/step3/02-observed-target.md`

```text
Objective: build a trustworthy observed reference before applying any development.

1. Resolve or explicitly qualify the monetary interpretation. Check paid versus
   incurred, case reserves, recovery treatment, excess and status exclusions.
   On the audited source, closed incurred equals paid and case amounts are
   nonnegative; those checks do not establish future reserve adequacy.
2. Under the declared gross-of-recoveries interpretation, observed net incurred
   is incurred_to_date minus recorded recoveries. Do not subtract excess twice.
   Exclude declined/repudiated claims explicitly and report unknown statuses.
   Keep paid, incurred, case and observed recoveries as separate source quantities.
3. Aggregate matched accepted claims by row_id and by row_id/peril. Left join
   back to every clean training policy row, preserving zero-claim rows, original
   row identity and corrected exposure. Count accepted reported claims separately
   from positive-cost rows; do not lose accepted zero-cost claims.
4. Reconcile source -> linkage groups -> status groups -> peril/line/year -> row
   response. Use a documented monetary tolerance consistent with source precision.
   Investigate negative net amounts; never clip, add an epsilon to labels or
   round claims solely to force reconciliation. Observed zeros remain valid.
5. Reproduce the three line totals and 744,330,677.04 CU combined reference if
   input hashes and interpretation are unchanged. Retain the 11.89m BI claim.
6. Test multiple claims/perils on one row, zero-claim rows, accepted zero amounts,
   repudiations, recovery subtraction, excess non-duplication and conservation.

Acceptance: all original training rows survive, financial totals reconcile and
the response is named observed_net_incurred, not actual_ultimate. Next: S3-03.
```

## S3-03 — Diagnose maturity and what can be identified

Prompt file: `prompts/step3/03-maturity-diagnostics.md`

```text
Objective: identify where and why the observed reference may differ from ultimate.

1. Calculate reporting delay = report_date - loss_date and maximum observable
   delay = valuation_date - loss_date. Report invalid/negative dates and reports
   after the valuation cutoff rather than accepting future observations.
2. Build count-only accident/reporting period tables and diagnostics by line,
   peril, loss cohort, claim age and status. Report counts, open shares, paid,
   incurred, case amounts, recoveries and tail concentration. Use denominators
   consistently: open-claim count share differs from open incurred share.
3. Explain right truncation: claims with reporting delay longer than their
   observable age are missing. An empirical CDF of observed delays is a diagnostic,
   not an unbiased reporting-completeness factor. Prioritize BI and subsidence;
   examine material case reserves on other perils too.
4. Explore severity/lag and recovery/settlement associations while stating their
   selection and maturity biases. Lower recent-year mean severity and a high
   open share do not identify the case-reserve uplift needed.
5. State the data limitation: there is one financial snapshot, no historic paid/
   incurred transaction triangle and no later financial outcome for today's
   open claims. Do not infer close dates or fabricate past case reserves.
6. Write docs/step3/maturity-diagnostics.md and an identification register:
   measurable, estimable under explicit assumptions, and not identified here.
   Keep large-loss sensitivity separate from deleting/capping the source loss.

Acceptance: maturity priorities and their evidential limits are explicit;
reporting, case adequacy and recoveries have not been conflated. Next: S3-04.
```

## S3-04 — Estimate reporting completeness, with truncation

Prompt file: `prompts/step3/04-reporting-completeness.md`

```text
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
```

## S3-05 — Specify reported-claim and recovery scenarios

Prompt file: `prompts/step3/05-case-recovery-scenarios.md`

```text
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
```

## S3-06 — Assemble development candidates without inventing outcomes

Prompt file: `prompts/step3/06-target-candidates.md`

```text
Objective: publish useful observed targets and conditional maturity candidates
while preserving exactly what is known and what is assumed.

1. Keep observed_net_incurred unchanged. Assemble each candidate from separately
   named reported-claim development, unreported net loss and future-recovery
   components. Include target version, financial-basis status, fit cutoff,
   assumptions, eligibility and provenance. Do not manufacture 2025 labels.
2. Prefer retaining reported counts, per-peril completeness/effective exposure
   and claim severity candidates as explicit inputs for later model choices.
   Do not force a monetary adjustment merely because a count factor exists.
3. An optional monetary inverse-reporting candidate is allowed only under
   documented assumptions about delay and net ultimate amount. For example,
   summing u_reported,j / q_j with q_j=F_k(cutoff-loss_date_j) over matched
   reported claims is a weighted proxy under conditional independence and
   positivity assumptions. It is not the realised hidden loss on that row.
   If amount depends materially on delay, a count CDF alone is insufficient.
4. For that candidate, reporting allowance is the difference between weighted
   reported net-ultimate cost and its unweighted counterpart. Do not also add
   a second cohort IBNR reserve. Future recoveries on unreported claims must
   already be reflected in their assumed net severity, not deducted twice.
   Do not silently cap weights; unsupported values require a documented
   alternative or an unavailable-candidate status.
5. Rows with no observed claims can remain zero in a sparse weighted proxy;
   that is not a declaration that they have no IBNR. Do not allocate hidden
   claims to specific policies or smear a portfolio reserve across all rows
   and then call that ground truth. Any alternative allocation must be separately
   declared and must not become its own independent validation evidence.
6. Reconcile components by row/peril/line/cohort and verify that full reporting,
   a=1 and no future recovery reproduce the observed reference. Ensure monetary
   targets remain period amounts; exposure is not applied twice. Record reference,
   reporting-only and supported scenario variants without selecting one by
   scoring against its own manufactured targets.
7. Full-snapshot diagnostic fits must be labelled accordingly. Export fit/transform
   interfaces and provenance so Step 4 can refit on permitted data; do not hand
   a full-data learned factor to a later fold as if it were leakage-free.

Acceptance: usable observed responses and transparent reserving outputs exist.
Conditional candidates are explicitly proxies. A definitive ultimate target
can remain unselected when the data cannot justify it. Next: S3-07.
```

## S3-07 — Verify, challenge and hand off to validation

Prompt file: `prompts/step3/07-acceptance.md`

```text
Objective: provide reproducible claim/target construction and an honest maturity handoff.

1. Add make step3-check for nonzero synthetic tests of linkage, accounting,
   aggregation, delay likelihood/cutoffs, scenario identities and leakage/failure
   cases. Keep prior Step 1/2 checks passing. CI must require no competition data.
2. Add a full local command, such as make build-targets, using the Step 2 manifest
   and the target/scenario config. Write local crosswalks, quarantine tables,
   observed targets, completeness outputs, candidate scenarios and component
   reconciliations under outputs/step3/. Use atomic output publication and
   provenance for actual code/config/input versions, including uncommitted edits.
3. Verify row identity/count conservation, zero-row preservation, no duplicated
   claims, accounting identities and raw/clean input immutability. Same-hash,
   same-basis inputs should reconcile the reference totals; investigate rather
   than hard-code/relax discrepancies. Reruns must not reapply adjustments twice.
4. Challenge count-versus-amount completeness, truncated tails, calendar/mix
   changes, selected closed severities/recoveries, reserve releases, the extreme
   BI claim, model-dependent IBNR allocation, double adjustments and artificial
   historical financial snapshots. Fix in-scope defects; document remaining limits.
5. Write docs/step3/acceptance.md and the component-level aggregate report. State
   separately: deterministic observed-target readiness; delay-estimator evidence;
   scenario-engine verification; assumptions and human decisions still pending.
   A passing engine does not establish a financially correct selected scenario.
6. Update DATA_CARD.md, assumptions, status, the exact environment lock and
   PROMPT_LOGS.md. Report actual tests and numerical scenario impacts; do not
   fabricate actuarial sign-off, efficiency gains, ultimate accuracy or CI runs.
7. Hand Step 4 the observed targets, component/proxy versions, immutable manifests,
   estimator refit interfaces, cutoff rules and unresolved assumptions. Do not
   generate split manifests, tune pricing models or evaluate on fabricated
   ultimate labels as if they were independent truth. Do not commit or push.

Acceptance: deterministic outputs reconcile, synthetic and actual-data checks
are reported separately, assumptions remain visible, and the next phase can
compare models without silently inheriting full-data adjustment leakage.
```

## What completion means

| Component | Evidence required |
| --- | --- |
| Linkage | Every source claim has one disjoint disposition; interval boundaries tested |
| Observed response | All training rows preserved; source-to-row accounting reconciles |
| Reporting | Truncation handled; estimability and finite-follow-up checks documented |
| Case/recovery treatment | Component formulas tested; parameter rationale/status visible |
| Conditional target candidates | No double adjustment; no fabricated row-level ultimate outcomes |
| Reproducibility | Local rebuild, immutable inputs, versioned config/provenance and synthetic CI checks |
| Step 4 readiness | Refit interfaces, cutoff rules, target versions and limitations transferred |

Expected ultimate at policy level is still the pricing goal. The response data produced here are measured references and assumption-dependent estimators of that goal. The distinction must survive in filenames, schemas, reports and later validation.

## Primary technical references

- Bücher and Rosenstock, *Micro-level prediction of outstanding claim counts based on novel mixture models and neural networks*, European Actuarial Journal, especially the observation scheme and truncated conditional likelihood: https://link.springer.com/article/10.1007/s13385-022-00314-4 . Use the statistical truncation principle; this guide does not prescribe their neural-network architecture.
- Verbelen, Antonio, Claeskens and Crevecoeur, *Modeling the occurrence of events subject to a reporting delay via an EM algorithm*: https://arxiv.org/abs/1909.08336 . A reference for separating occurrence/reporting and checking count nowcasts, not proof of any monetary factor for this dataset.
- Official competition definitions and source-status records are in the repository's docs/step1/source-register.md and linked Kaggle pages. Recheck the financial field definitions before asserting that one subtraction convention is verified.
