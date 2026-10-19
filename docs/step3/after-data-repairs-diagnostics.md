# Step 3 diagnostics after Step 2 repairs

## Scope and authoritative definition

The dated project source register records the official metric as **“Tweedie D² score (power = 1.5)”** and the submission illustration as:

```text
row_id, prediction
M02409311,583.47
B01834522,412.10
```

Its dated overview paraphrase describes the requested value as policy-period expected ultimate cost, net of excess/recoveries and excluding declined claims. The detailed field basis and scorer implementation are not available in the local evidence. Therefore the observed net-incurred baseline below is not asserted to be the official target or ultimate loss.

## Inputs and reconciliation

`scripts/run_step3_diagnostics.py` consumed only the Step 2 repair output, not raw inputs:

- `model/training-model-table.parquet` — SHA-256 `26fe66401b44aff157754c9166c8117b8345c6e94c1d88a6a87bc8dda986d793`
- `claims/matched.parquet` — SHA-256 `994815e1c39e4b37bd55a8a12e0cf4e9b65d542052fed075a8f855841f55cd85`
- `claims/quarantined.parquet` — SHA-256 `feef26b600fc7cbb6ab651929a8961af1cd2ae265cf12cedae6c90683aa77a1c`

The diagnostic accepted 160,432 matched open/closed claims and reconciled their `incurred_to_date - recoveries` to all 2,409,311 training policy rows. The maximum per-row difference was `0.0`; the observed net-incurred total was 741,156,868.43 CU.

The repair model table preserves source exposure in its `exposure` field. It also contains the separately named Step 2 ACT/365 result, `exposure_clean`; `exposure` equalled `exposure_raw` for every row. The diagnostic deliberately uses `exposure_clean`, giving corrected total exposure 1,968,577.0591: 590,560.1951 buildings, 590,859.3077 contents and 787,157.5563 motor. This is a transparent diagnostic-basis choice, not a modification of Step 2 data or a human approval of the convention.

## Quarantine and reporting observations

The 413 quarantined claims total 1,721,459.84 CU of snapshot net incurred, and are excluded from the baseline pending investigation. They comprise 67 buildings, 50 contents and 296 motor claims; three, one and eleven of those counts are open respectively.

Among the known snapshot claims, weighted count fractions reported by their accident-year end were 92.91% (2021), 93.45% (2022), 93.71% (2023) and 100.00% (2024). The 2024 value is mechanically expected at a 31 December 2024 snapshot and is not completeness evidence. The clearest conditional late-reporting signals are motor bodily injury (54.94%, 56.70%, 60.22% for 2021–2023) and buildings subsidence (68.44%, 65.37%, 71.05%). These fractions condition on claims present in the snapshot; they do not estimate unreported claim counts or ultimate amount completeness.

## Limitations and next step

Only one financial snapshot is available. It cannot reconstruct historical reserve valuations, payment development, future recoveries, or unreported amounts, and snapshot labels could leak future information in time-based validation. No IBNR factor, case-reserve multiplier, future-recovery assumption, trend, scenario, prediction or submission was created. Next prompt: the user must explicitly select a Step 3 follow-on prompt; do not treat this diagnostic as target approval.
