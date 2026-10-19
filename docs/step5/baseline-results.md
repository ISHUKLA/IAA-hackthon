# Step 5 baseline results

All figures use the repaired deduplicated claim candidate and the `repaired_observed_net_incurred_snapshot_2024-12-31` response. They are retrospective snapshot-proxy comparisons, not ultimate-loss validation.

| Fold | Model | Mean deviance | Pooled D² | Reference A/E |
| --- | --- | ---: | ---: | ---: |
| F2023 | B0 global mean | 116.741540 | -0.000009 | 1.007740 |
| F2023 | B1 line exposure rate | 106.616810 | 0.086719 | 1.058715 |
| F2023 | B2 premium comparator | 107.938563 | 0.075397 | 0.953064 |
| F2023 | B3 compact GLM | 104.041285 | 0.108781 | 1.042335 |
| F2024 | B0 global mean | 109.506007 | -0.002342 | 0.883728 |
| F2024 | B1 line exposure rate | 101.500296 | 0.070937 | 0.912337 |
| F2024 | B2 premium comparator | 102.264710 | 0.063940 | 0.820412 |
| F2024 | B3 compact GLM | 99.947988 | 0.085145 | 0.903757 |

B3 improved pooled mean deviance over B1 by 2.575525 on F2023 and 1.552308 on F2024. All line GLMs converged in three Newton–Cholesky iterations. The complete S5 rebuild took 36.93 seconds. B2 is a supplied policy-period premium comparator only; it is not part of the technical core.

The returning/new split is material. On F2023, B3 mean deviance/A/E was 107.380240/1.031405 for 530,424 returning policies and 85.579450/1.146472 for 95,931 new policies. On F2024 it was 103.811844/0.891456 for 530,517 returning policies and 78.522496/1.021082 for 95,673 new policies. Policy- and customer-return flags coincide with the supplied `new_business` split in these folds; this is a measured identity, not a general assumption.

The 11,894,276.93 CU motor bodily-injury claim remains in the F2023 primary result. In a separate mechanical sensitivity that subtracts only that claim from its linked row while holding all predictions and rows fixed, B3 mean deviance falls from 104.041285 to 101.596694. This concentration does not justify deleting or down-weighting the claim.

The ignored `baseline_pipeline_check.csv` has 626,639 rows, exact sample ID coverage/order, finite nonnegative predictions and SHA-256 `a7eef9d229d969a01d432213fc7dd719d3fc0d861de9d8605892d11ce31dc012`. It is B1 trained on 2021–2024 proxy responses, not a final competition prediction.

Reproduce:

```text
make step5-check PYTHON=.venv/bin/python
make run-baselines PYTHON=.venv/bin/python DATA_DIR='/path/to/competition/data'
make step5-acceptance PYTHON=.venv/bin/python
make step6-diagnostics PYTHON=.venv/bin/python
```
