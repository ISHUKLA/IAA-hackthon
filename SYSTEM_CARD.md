# System Card — Step 1 contract package

## Implemented components

- `doctor`: presence-only check for eleven local inputs.
- `inventory`: read-only Parquet schema, metadata, hash, required-field and key-coverage evidence; machine output is ignored.
- `iaa_hackathon.metrics`: fixed Tweedie power 1.5 with explicit weight and undefined-case handling.
- `iaa_hackathon.submission`: structural frame/CSV validation against exact sample IDs, with separate official-zero and local-strict-positive policies.
- `make step1-check`: raw-data-free schema, example and nonzero behavioral-test gate.

## Environment and controls

The exact tested Python 3.12 dependency versions are in `requirements/step1-py312.lock`; the recorded verification platform is macOS 26.6.2 x86_64. Platform-specific wheels may differ. CI is defined with read-only repository permission and synthetic tests, but GitHub execution has not been observed because no commit or push was requested.

Raw inputs, archives, local environments and generated row-level outputs are excluded from Git. The utilities do not train models, publish, submit or contact organisers. Exceptions fail explicitly. Human actuarial acceptance remains pending and is not replaced by automated or AI review.
