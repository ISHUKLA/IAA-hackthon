# Reporting-delay and count-completeness estimator

## Model

The estimator uses one discrete geometric family on integer days, independently for each observed line/peril group; bodily injury is not pooled with glass. Its count population is every exactly matched claim reported by the cutoff, with no final-status exclusion; status affects the observed monetary response, not historical count visibility. For claim `j`, `D` is report date minus loss date and `A` is fit cutoff minus loss date. The right-truncated log-likelihood contribution is `log f(D) - log F(A)` conditional on `D <= A`. Day zero is valid. Fits record their population and cutoff and are labelled `full_snapshot_diagnostic_not_fold_safe`.

All 15 line/peril fits converged. Full-snapshot daily probabilities range from 0.005401 for motor bodily injury and 0.007576 for buildings subsidence to 0.136031 for buildings fire. These geometric tails are parametric extrapolations, not observed truth.

For each eligible policy row/peril, the build averages `F(age)` over all inclusive covered dates under a uniform daily occurrence assumption and writes effective reported exposure as clean exposure times that completeness. Prefix-sum lookup avoids day-by-day row loops. The output contains 12,032,664 row/peril records. Mean completeness is 0.8669 for motor bodily injury and 0.9044 for subsidence; other groups are roughly 0.9806–0.9944. Very recent dates can have much lower values, and no inverse weight is silently floored or capped.

## Finite-follow-up checks

The end-2022 fit predicted 82,391.5 reports across the 15 groups for loss dates available then, compared with 82,507 actually reported by end-2024; mean absolute group error was 37.8 claims. The end-2023 fit predicted 123,911.2 against 123,919 reported by end-2024; mean absolute group error was 31.3. BI was over-predicted by 219.1 and 180.1 in those checks; subsidence was under-predicted by 21.7 at end-2022 and over-predicted by 42.3 at end-2023.

The comparison endpoint is finite follow-up, not ultimate. Calendar/mix instability, seasonality and the uniform daily assumption remain limitations. Count completeness does not establish monetary amount completeness or case adequacy. Step 4 must refit within each permitted training population and cutoff.
