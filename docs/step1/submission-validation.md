# Submission validation boundary

`iaa_hackathon.submission` validates structure only. It does not create predictions, alter the sample, contact Kaggle or establish that a file was accepted by the competition.

The official-mode boundary requires exactly `row_id,prediction` in that order, the declared row count, unique string identifiers with exact sample-key membership, and finite numeric predictions greater than or equal to zero. Valid-looking `M`, `B` or `C` prefixes are insufficient; membership is exact, and contents identifiers use `C`. Row order may differ without invalidating membership. `order_like_sample` supplies sample order as the deterministic later generation convention.

The optional strict-positive mode adds `prediction > 0` for local compatibility with standard Tweedie scoring at power 1.5. It does not rewrite or floor a zero and does not reinterpret the official nonnegative boundary.

For a later real candidate, read the real sample's `row_id` column as text, load `SubmissionRules.from_problem_contract()`, call `validate_submission_csv`, and record the result and file hash. CSV rereading preserves leading zeros and catches accidental index/extra columns. Prompt 05 does not perform that future application because no competition predictions exist.
