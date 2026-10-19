# Step 4 challenge review

Automated tests reject duplicate/missing prediction IDs, response-version mismatch, nonpositive local-metric predictions, cross-year periods and test-year fold inclusion. The feature registry excludes response fields, contacts and renewal decisions; weather and telematics remain conditional. The repaired and raw Step 3 universes are deliberately not combined. These are automated checks, not human approval.

Remaining conceptual limits are later-valued financial labels, maturity differences, snapshot deduplication hindsight, unknown feature timestamps and the large BI claim. Returning risks are legitimate in the renewal setting; they are not row leakage.
