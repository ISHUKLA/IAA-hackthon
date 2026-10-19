# Step 6 feature results

| Line / block | F2023 deviance change vs B3 | F2023 decision | F2024 change for frozen line candidate |
| --- | ---: | --- | ---: |
| Motor age nonlinearity | -1.010373 | retain | — |
| Motor vehicle/mileage | +0.012478 | reject | — |
| Motor missingness | -0.000189 | retain | — |
| Motor selected combination | -1.010532 | freeze | -1.106051 |
| Buildings log sum insured | -0.203432 | retain, adoption pending | — |
| Buildings occupancy/security | -0.018352 | retain | — |
| Buildings construction interaction | +0.007942 | reject | — |
| Buildings selected combination | -0.225088 | freeze | -0.042031 |
| Contents log sum insured | -0.157520 | retain, adoption pending | — |
| Contents household use | -0.009024 | retain | — |
| Contents security/value | -0.061838 | retain | — |
| Contents selected combination | -0.227996 | freeze | -0.155141 |

The selected combined candidate improved pooled F2023 mean deviance from 104.041285 to 103.496088 and D² from 0.108781 to 0.113452. Frozen F2024 mean deviance improved from 99.947988 to 99.439308 and D² from 0.085145 to 0.089801. F2024 A/E remained low at 0.908890, consistent with material recent-year maturity/calibration uncertainty rather than evidence of ultimate accuracy. The feature experiment took 61.89 seconds; every fitted candidate converged.

The feature candidate improved both returning and new-policy segments. On F2023, returning mean deviance/A/E moved from 107.380240/1.031405 to 106.832378/1.039999; new moved from 85.579450/1.146472 to 85.048990/1.143532. On F2024, returning moved from 103.811844/0.891456 to 103.243766/0.897049; new moved from 78.522496/1.021082 to 78.343182/1.021134. Policy and customer return classifications coincide here.

The retained extreme F2023 bodily-injury claim remains in selection and scoring. Subtracting only its 11,894,276.93 CU amount in the separate fixed-prediction sensitivity changes S6 mean deviance from 103.496088 to 101.088331; S6 still improves on S5 in both the primary and sensitivity comparisons. The analogous largest-claim F2024 sensitivity changes S6 mean deviance from 99.439308 to 99.311253. These are diagnostics, not alternative targets.

Rejected blocks are retained as negative evidence. Telematics, contemporaneous weather, monetary/final-status history and repaired scenario sensitivity were not tested because their timing or consistent response universe is unavailable.

Reproduce:

```text
make step6-check PYTHON=.venv/bin/python
make run-feature-experiments PYTHON=.venv/bin/python
make step6-diagnostics PYTHON=.venv/bin/python
make step6-acceptance PYTHON=.venv/bin/python
```
