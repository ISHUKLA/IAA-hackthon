# Step 4 feature availability

`configs/feature_registry.json` is an explicit allowlist. Same-period responses, claim/linkage data, identifiers, exposures and known training-only/post-period columns are excluded. Telematics score and whole-year weather are conditional rather than core because their timing is not established. Monetary and final-status historical features are unavailable; a count history requires report-date visibility before `period_start`. Target encoding is disabled. The registry preserves provisional Step 2 flags without repairing them.
