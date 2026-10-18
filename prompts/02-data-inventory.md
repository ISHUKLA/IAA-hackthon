# Prompt 02 — Verify input readiness without changing data

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Confirm that the local files support the proposed contract. Do not perform full cleaning, target construction or reserving.

## Procedure
1. Resolve IAA_DATA_DIR or the explicitly supplied directory. Run the doctor. Install only the dependencies needed for Parquet metadata/key inspection, recording changes.
2. Add a read-only inventory command. Read the eleven Parquet schemas, row counts and SHA256 hashes; compare with docs/evidence/expected-manifest.json. Reuse hashes within this run rather than repeatedly scanning unchanged files.
3. Inspect only necessary columns to confirm training/test date ranges, policy-row key, loss/report dates, exposure, incurred/recovery/status fields and sample columns. Check test row IDs for uniqueness and exact sample coverage. Sample predictions are placeholders, not labels.
4. Write the machine-specific inventory under outputs/step1/. Write a reviewed aggregate summary in docs/step1/data-readiness.md with discrepancies and explicit status. Do not commit local absolute paths or input records.
5. Treat reference audit anomalies as measured earlier, not newly reverified unless actually checked. A hash difference triggers reconciliation before relying on the old findings; never overwrite the reference manifest to make the check pass.
6. Document future requirements for exposure, IDs, linkage, recovery and maturity without executing those repairs here.

## Acceptance
File identities and required fields are established or discrepancies are reported. Train/test dates, 626,639 test rows and sample key coverage are verified on this machine. Raw hashes are unchanged after inspection. Next: Prompt 03.
