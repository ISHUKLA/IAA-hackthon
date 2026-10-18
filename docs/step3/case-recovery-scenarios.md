# Reported-claim case and recovery scenarios

For paid `P`, incurred `I`, case reserve `C = I-P`, recorded recoveries `R`, case multiplier `a` and additional future recovery `R_future`, the engine computes `P + a*C - R - R_future`. Thus `a=1` and zero future recovery reproduce observed net incurred exactly. The multiplier applies only to case reserve; paid is untouched and recorded recovery is subtracted once. Trend is disabled.

| Scenario | Case multiplier | Total (CU) | Impact from observed (CU) |
| --- | ---: | ---: | ---: |
| Neutral reference | 1.0 | 744,330,677.04 | 0.00 |
| Illustrative 20% reserve release | 0.8 | 726,279,894.76 | -18,050,782.28 |
| Illustrative 20% reserve strengthening | 1.2 | 762,381,459.32 | +18,050,782.28 |

The largest BI claim contributes 11,894,276.93 CU in the reference, 9,663,175.44 CU under release and 14,125,378.42 CU under strengthening. This sensitivity is reported explicitly because it is material.

The 0.8 and 1.2 values are illustrative stresses, not confidence bounds or estimated adequacy factors. Future recovery is zero in all three scenarios because it is not identified from this snapshot, not because zero is known to be correct. Closed-claim recoveries for own damage and theft are selected evidence and do not justify a forecast for current open claims. Invalid parameters and negative net outcomes fail rather than being clipped.

