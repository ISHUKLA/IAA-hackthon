# Observed response and accounting

## Provisional basis

The implemented audit reference is `observed_net_incurred = incurred_to_date - recoveries` for exactly matched `closed` and `open` claims. It is valid only under the still-unverified interpretation that incurred is gross of recorded recoveries and already reflects policy excess. Policy excess is not deducted again. There are 1,711 source `repudiated` claims, of which 1,707 are matched and explicitly excluded under a provisional mapping to the official declined-claim exclusion; their recorded amounts are all zero.

This is a 31 December 2024 snapshot reference, not `actual_ultimate`. Closed incurred equalling paid and nonnegative case balances are useful accounting checks, but not evidence that open reserves are adequate.

## Actual reconciliation

| Line | Accepted claims | Observed net incurred (CU) |
| --- | ---: | ---: |
| Motor | 110,901 | 430,595,512.14 |
| Buildings | 26,375 | 247,768,586.05 |
| Contents | 23,753 | 65,966,578.85 |
| Total | 161,029 | 744,330,677.04 |

All 2,409,311 training policy rows survive the left join; 2,262,942 have zero accepted claims. Accepted zero-cost claims are counted separately from positive-cost claims. Row and row/peril amounts both reconcile to 74,433,067,704 minor units. The 11,894,276.93 CU bodily-injury claim is retained unchanged.

The competing already-net-incurred interpretation remains unresolved. Selecting it would change the reference by 27,613,464.36 CU on the matched accepted population; no numerical convenience or model score was used to decide the basis.
