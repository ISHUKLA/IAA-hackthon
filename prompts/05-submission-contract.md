# Prompt 05 — Verify submission structure without generating predictions

Execute only this prompt. Follow AGENTS.md. Perform the reversible work needed to complete this scope; do not execute later prompts. Preserve unrelated files and original briefs. At the end report changed files, actual verification results, unresolved assumptions and the next prompt. Never mark human approval on the user's behalf.

## Objective
Implement the submission contract checker and synthetic tests. Do not create a competition prediction file.

## Procedure
1. Add src/iaa_hackathon/submission.py to validate a candidate frame/file against sample IDs and a declared contract. Separate official nonnegativity from optional strict-positive scoring compatibility.
2. Require exact two column names, expected row count, unique identifiers, exact ID coverage, finite numeric predictions, and no index column. Do not accept valid-looking M/B/C prefixes as a substitute for exact ID membership. Contents prefixes are C.
3. Permit IDs in a different order if the official contract does not require order, while providing sample order as the later generation convention. The displayed header's whitespace does not create a leading-space column name.
4. Add tiny synthetic fixtures/tests covering valid input; reordered IDs; missing/extra/duplicate IDs; wrong or extra columns; nonnumeric/NaN/infinite/negative values; and zero predictions under each declared positivity policy. Parameterize expected fixture rows rather than demanding 626,639 synthetic records.
5. Test CSV rereading so accidental index columns and identifier coercion are caught. Use synthetic records only.
6. Document how this checker will later be applied to the real sample. Do not derive predictions or claim an upload has been accepted.

## Acceptance
Behavioral tests establish the actual boundary rules, including zeros and ordering. No competition data or row-level output is staged in Git. Next: Prompt 06.
