# Step 1 problem definition

## Contract status and sources

This is the prediction, exposure, scoring and submission contract for Part 1. It is grounded in the official requirements catalogued in `docs/step1/source-register.md` and the byte-verified local fields in `docs/step1/data-readiness.md`. The audited exposure behavior and absence of ultimate labels are measured evidence from `docs/evidence/known-findings.md`. The inclusive ACT/365 correction, pooled unweighted local scoring and strict-positive local scorer policy are proposals, not organiser rules. Exact competition pooling and weighting, supplied-financial-field interpretation, and all ultimate-development assumptions remain unresolved. Human actuarial review is pending.

## Prediction grain and claim allocation

One prediction belongs to one `row_id`: a covered policy-period row. An eligible claim must have the same line and `policy_id`, and its `loss_date` must fall inclusively between `period_start` and `period_end`. A claim arising in May 2025 therefore belongs to a January–June 2025 row even if it is reported in February 2026; a July loss does not belong to that row. Report or payment dates do not move the loss to another coverage period. Declined or repudiated claims are excluded, and a claim outside supplied coverage is quarantined rather than forced onto the nearest row.

## Expected net ultimate cost

The target is expected total ultimate claim cost for the covered row period, in the competition's fictional currency and net of policy excess and recoveries. It is an expectation, not a promise of one policy's realized result. Frequency and severity are two views of the same expectation: a 10% claim probability multiplied by 1,000 CU conditional cost is 100 CU expected cost, even though the individual policy will most likely have a zero observed outcome.

Actual ultimate labels are not supplied. Keep these quantities distinct:

- observed net incurred at the supplied 31 December 2024 valuation;
- unreported losses;
- further development on reported claims;
- future recoveries; and
- trend to the 2025 cost level.

The latter four require future estimation or assumptions. Before constructing any target, reconcile whether supplied incurred amounts already reflect excess and recoveries. Never deduct an excess or recovery twice.

## Exposure and output scale

The output is row-period cost, not an annual rate left unscaled. Exposure is applied exactly once. For example, an annual expected cost of 200 CU multiplied by 0.25 exposure gives a row-period expected cost of 50 CU.

The audited candidate convention is inclusive ACT/365: `((period_end - period_start).days + 1) / 365`, rounded to four decimal places. Its status is proposed because the organisers have not confirmed that convention. A later cleaning step must preserve raw exposure, add a separately named derived exposure and correction flag, and reconcile totals reversibly. This contract performs no correction.

## Metric

The official metric name is **“Tweedie D² score (power = 1.5)”**, and higher is better. Under the documented standard scikit-learn semantics, D² is one minus model mean Tweedie deviance divided by null mean Tweedie deviance. Model deviance 70 against null deviance 100 gives `1 - 70/100 = 0.3`.

The mathematical null uses the mean of `y_true` on the exact rows being scored, with the same weights if weights are supplied. That calculation is a benchmark denominator, not a feature, not a training estimate, and never a reason to use hidden test outcomes. A practical constant model instead estimates its value from training data only and applies it unchanged to validation or test data; it need not score zero on a different population.

The competition's row/line pooling and weighting are unresolved. Until primary evidence establishes them, local reports may use a clearly labelled provisional pooled, unweighted score. They must not call that choice official.

At power 1.5, multiplying both an annual rate target and prediction by exposure multiplies each observation's deviance by `sqrt(exposure)`. Consequently, the unweighted row-loss **deviance total** can be represented by rate deviance weighted by `sqrt(exposure)`, apart from the mean's normalizing constant. That statement does not automatically make the two D² scores identical: their null denominators must be defined consistently. Ordinary exposure-weighted rate fitting is a different objective.

## Submission boundary

A competition submission has exactly two columns named `row_id` and `prediction`, 626,639 rows, unique identifiers with exact combined test-key coverage, and finite numeric predictions. The official lower bound is zero. Local use of standard Tweedie scoring at power 1.5 requires strictly positive predictions and will enforce that separately; this is a compatibility rule, not a claim that the published submission minimum is greater than zero.

Order is not established as an official validity requirement. Later generation should use sample-submission order as a deterministic convention. The whitespace in the published display does not create a leading-space column name.

Portfolio calibration is necessary but not sufficient. One thousand policies at 50 CU each total 50,000 CU, but the same total can conceal risk groups that should receive 10 CU and 90 CU. Segment diagnostics therefore remain necessary even when totals agree.

## Actuarial choices requiring human review

- Whether inclusive ACT/365 is the approved corrected exposure convention and rounding rule.
- How supplied incurred, paid, excess and recovery fields combine on the observed net basis.
- Assumptions for unreported losses, reported-claim development, future recoveries and 2025 trend.
- Treatment of claims outside supplied coverage.
- Whether pooled, unweighted local scoring is fit for model comparison while official pooling and weights remain unknown.
- Whether strict-positive predictions should be the operational file policy or only the local scoring policy.
- How immature 2024 outcomes may be used in validation without representing them as ultimate truth.

No human choice is marked approved. Data repair, claim/financial reconciliation, target development, maturity modelling, split creation, model training, prediction generation and upload are outside Step 1 contract construction.
