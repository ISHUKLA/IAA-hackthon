# Step 2 sum-insured unit review

## Reverified evidence

The buildings and contents distributions have clear observed gaps around the prior diagnostic separators. These separators are diagnostics, not policy limits.

| Line | Largest ordinary value | Smallest high-cluster value | High-cluster values after division by 1,000 |
| --- | ---: | ---: | ---: |
| Buildings | 1,061,000 | 52,000,000 | 52,000–594,000 |
| Contents | 346,700 | 8,200,000 | 8,200–152,600 |

Across train and test, 1,703 of 1,765 buildings candidates and 1,716 of 1,762 contents candidates have another ordinary-scale observation for the same policy. Of the limited-history remainder, 61 of 62 buildings rows and all 46 contents rows are marked new business. This supports—but does not prove—the factor-of-1,000 interpretation for sparse histories.

## Candidate impact

| Source | Candidate rows |
| --- | ---: |
| Buildings train | 1,395 |
| Buildings test | 370 |
| Contents train | 1,402 |
| Contents test | 360 |

The pipeline preserves `sum_insured_raw`, creates a separately named candidate, flag, proposed divisor, reason and `status='inferred'`, and leaves ordinary values unchanged. No source field is overwritten; the rule does not touch claims, premium or other financial fields. An exact separator value is treated as ambiguous, and nulls remain null. Repeated execution derives from the raw field and cannot divide twice.

Human adoption of the candidate as canonical downstream data is pending. The 11.89 million CU bodily-injury claim is outside this rule and is not treated as a unit error.

