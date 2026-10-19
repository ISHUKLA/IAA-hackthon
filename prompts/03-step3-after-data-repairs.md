# Step 3: observed baseline and reporting diagnostics

First read the competition's authoritative target, evaluation, and data documentation available in this project. Quote their relevant definitions and mark anything unavailable as unverified. Do not assume observed net incurred is the official target.

Run Step 2 first and review its audit, duplicate register and quarantine. Use its outputs, not raw inputs, for Step 3. Run:

```
python scripts/run_step3_diagnostics.py --step2-dir <step2-output-directory> --output-dir <new-step3-output-directory>
```

Inspect the output reconciliation, corrected exposure totals, and quarantine summary. Investigate disagreements rather than silently fixing them. Do not overwrite source files. Explain whether the observed baseline agrees with the official target definition, including exposure and financial basis. Identify timing/leakage limitations and document what cannot be established from a single financial snapshot.

Use reporting diagnostics to assess whether late reporting might matter; they are conditional on claims present in the snapshot and are not estimates of true ultimate completeness. Do not apply IBNR factors, future recovery assumptions, claims development factors, or cost trends without an explicit, documented rationale and validation. If justified, compare separately labelled, parameterized alternatives against the unadjusted baseline and construct validation labels without future-information leakage where data permit. Do not call scenarios confidence intervals.

Report outputs, tests, open questions, and any deviations. Never submit predictions or modify external repositories unless explicitly instructed.
