# Step 2 customer-identifier reconciliation

## Rule and evidence

The reference `customers.parquet` contains 545,240 non-null, unique identifiers. Every value is exactly eight decimal characters; the range includes leading-zero values such as `05180324`. That observed reference, rather than a numeric assumption, defines the canonical representation.

The implemented rule preserves `customer_id` as `customer_id_raw`. An already canonical reference is retained; a shorter decimal string is left-padded to eight characters only when the result exists in the unique reference. Null, malformed, overlong and unresolved values remain visible with a reason and do not become the strings `nan` or `None`. No fuzzy match or invented customer is allowed.

## Actual reconciliation

| Source | Rows | Matched before | Leading-zero repairs | Matched after | Unresolved after |
| --- | ---: | ---: | ---: | ---: | ---: |
| Motor train | 979,968 | 881,858 | 98,110 | 979,968 | 0 |
| Motor test | 254,986 | 229,432 | 25,554 | 254,986 | 0 |
| Buildings train | 707,726 | 707,726 | 0 | 707,726 | 0 |
| Buildings test | 184,155 | 184,155 | 0 | 184,155 | 0 |
| Contents train | 721,617 | 721,617 | 0 | 721,617 | 0 |
| Contents test | 187,498 | 187,498 | 0 | 187,498 | 0 |

All policy row counts, `row_id`, `policy_id` and `address_id` values are preserved. Duplicate dimension keys fail the pipeline; repeated policy references to one customer remain valid.

Synthetic tests cover leading-zero recovery, canonical values, nulls, malformed and overlong strings, unresolved references, duplicate dimension keys, allowed many-to-one references and repeat application.

