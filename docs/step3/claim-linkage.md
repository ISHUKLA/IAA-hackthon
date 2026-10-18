# Claim linkage

## Rule and result

Claims are linked on exact `line` and `policy_id`, then on inclusive `period_start <= loss_date <= period_end`. Report dates and financial amounts do not select coverage. Source `claim_id` is unique and non-null, and no policy periods overlap within line/policy.

The actual build assigned 162,736 of 163,150 source claims to exactly one training policy row. The remaining 414 are before the first supplied coverage period; none was shifted to a renewal. There were no unknown-line, unknown-policy, after-coverage, gap, invalid-date or multiple-match records. Counts and paid/incurred/recovery minor units reconcile from the source into these disjoint groups in `outputs/step3/prepared/target-reconciliation.json`.

The ignored crosswalk retains source dates, status and amounts. Exceptions are also written separately, with their source quantities unchanged. Claim outcomes remain target-construction data and are not pricing features or test-row inputs.

## Verification and limitation

Synthetic tests cover inclusive boundaries, next-year reports, mid-term changes, gaps, wrong lines, unknown policies, overlaps and repeated claim IDs. Overlapping coverage and duplicate claims fail the strict build. These checks establish deterministic allocation for the supplied files; they do not establish that the available policy history starts before every real exposure.

