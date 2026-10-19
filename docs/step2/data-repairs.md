# Step 2 audited data repairs

The repair build is separate from the prior `outputs/step2/prepared/` layer so that existing Step 3 provenance remains intact. Run `make repair-step2 DATA_DIR=/path/to/raw` to publish ignored, atomic policy/claim/model-table outputs under `outputs/step2/repairs/`.

On the reference raw hashes, it retained 2,409,311 training and 626,639 test policies. Exposure repairs were 5,736 motor, 4,182 buildings and 4,311 contents training rows; no test exposure changed. Motor customer ID repairs were 98,110 training and 25,554 test rows. High-cluster sum-insured repaired candidates were 1,395/370 buildings and 1,402/360 contents train/test. Raw fields remain alongside derived values.

Exact equality across every supplied non-`claim_id` field found 604 duplicate claim groups and removed 604 copies, leaving 162,546 claims. Of those, 162,133 matched one inclusive loss-date coverage row and 413 were quarantined. Matched open/closed observed net incurred was 741,156,868.43 CU under the provisional incurred-less-recorded-recovery basis.

The supplied patch did not apply because the repository already has a different package layout; its behaviors were ported to the pandas/pyarrow project modules. Its compiled artifacts and separate Polars requirements file were intentionally omitted. The referenced audit report/bundle was not available locally; the supplied acceptance table was independently remeasured.

Pending definitions: NCB plausibility, electric engine capacity, zero mileage, customer snapshot timing, annual weather availability and written-premium basis. No model was trained and no final financial-basis approval is implied.
