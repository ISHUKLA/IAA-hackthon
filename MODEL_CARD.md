# Model Card — no model implemented

No predictive model, developed target, split manifest, fitted parameter, real-data validation score or competition prediction exists in Step 1.

Implemented evaluation infrastructure is limited to a fixed-power-1.5 wrapper around the standard scikit-learn mean Tweedie deviance and D² functions. It rejects invalid domains and exposes undefined D² rather than manufacturing a score. Local pooled/unweighted reporting is provisional because competition pooling and weights are unresolved.

Any later model card must identify the observed/proxy/adjusted target version; exposure treatment; as-of features; chronological split; parameters and seeds; pooled and line-level deviance/D²; calibration and segment diagnostics; maturity/recovery and large-loss sensitivities; runtime; prediction provenance; and human decisions. Passing Step 1 tests is not model validation.
