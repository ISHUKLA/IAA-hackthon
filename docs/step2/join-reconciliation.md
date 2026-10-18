# Step 2 dimension and weather joins

The pipeline validates the required dimension grains before checking policy linkage:

| Dimension | Key | Rows | Null keys | Duplicate keys |
| --- | --- | ---: | ---: | ---: |
| Customers | `customer_id` | 545,240 | 0 | 0 |
| Addresses | `address_id` | 575,983 | 0 | 0 |
| Weather | (`address_id`, `year`) | 2,879,915 | 0 | 0 |

All 3,035,950 policy rows match a cleaned customer reference, address reference and same-year address-weather reference. No policy period crosses calendar years in the supplied inputs. Every file retains its exact source order, row count, unique `row_id` coverage, original dates, premiums and exposure source values; no wide dimension matrix is materialized.

The reusable guarded join rejects duplicate dimension keys, validates many-to-one cardinality, isolates null foreign keys so they cannot match null dimension values, and verifies the `row_id` multiset. Synthetic tests cover duplicate customer/address-weather keys, address-year specificity, missing/null keys, reordered dimensions and duplicate policy IDs with distinct row IDs. Cross-year periods receive `cross_year_period` and no weather year; claim interval linkage remains Step 3 scope.

