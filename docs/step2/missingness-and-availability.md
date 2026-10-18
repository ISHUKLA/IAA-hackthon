# Step 2 missingness and feature availability

## Actual source profile

The ignored reconciliation contains null counts for every original field by source and policy-start year. The fields with observed missingness are:

| Source/year | Observed missing fields and counts |
| --- | --- |
| Motor 2021 | annual mileage 5,447; engine size 5,446; overnight parking 5,500; vehicle age 5,410; telematics score 190,669 |
| Motor 2022 | annual mileage 6,547; engine size 6,435; overnight parking 6,300; vehicle age 6,389; telematics score 223,630 |
| Motor 2023 | annual mileage 6,363; engine size 6,358; overnight parking 6,340; vehicle age 6,283; telematics score 222,344 |
| Motor 2024 | annual mileage 6,354; engine size 6,455; overnight parking 6,231; vehicle age 6,345; telematics score 221,580 |
| Motor 2025 test | annual mileage 6,271; engine size 6,440; overnight parking 6,398; vehicle age 6,316; telematics score 221,126 |
| Buildings 2021–2024 | days unoccupied: 3,825 / 4,501 / 4,643 / 4,618; smoke alarms: 4,088 / 4,570 / 4,716 / 4,493 |
| Buildings 2025 test | days unoccupied 4,586; smoke alarms 4,602 |
| Contents 2021–2024 | high-value items: 3,970 / 4,698 / 4,640 / 4,780; security level: 4,027 / 4,627 / 4,681 / 4,752 |
| Contents 2025 test | high-value items 4,707; security level 4,677 |

All 858,223 missing training telematics scores and all 221,126 missing test scores occur on non-opt-in rows. No opted-in missing score and no non-opt-in non-missing score was observed. Missing scores stay missing; they are not assigned a genuine score of zero.

The derived licence-start-age check flags 2,521 motor training rows and 639 test rows below 14. It is explicitly a fictional-market plausibility flag: the original driver age and years licensed are preserved, and no legal minimum or replacement value is asserted.

## Availability registry

| Field/group | Status | Reason |
| --- | --- | --- |
| `customer_service_contacts` | Quarantined | Strong outcome association but timing is not established |
| `renewal_decision` | Training-only | Absent from test; not a prospective test feature |
| Annual weather | Conditional | Supplied by address-year, but quote-time/prospective interpretation is unresolved |
| Customer/history aggregates | Conditional | Require as-of timing evidence before construction |
| Historical financial aggregates | Conditional | Require valuation-vintage evidence before construction |

No imputation, scaling, target encoding, learned category treatment or model feature matrix is implemented in Step 2. Original values and unknown categories remain present.

