# Model Card — Step 5/6 compact Tweedie GLMs

## Intended use and response

The implemented models compare simple pricing references on chronological policy folds. The response is repaired observed net incurred valued at 31 December 2024 and is labelled `retrospective_snapshot_proxy`; it is not observed ultimate. Scoring is provisional pooled, unweighted policy-period Tweedie D² at power 1.5.

## Models and exposure

B0 is the training mean; B1 is a training line loss rate times `exposure_clean`; B2 is a conditional supplied-premium comparator; B3 is one compact Tweedie GLM per line. B3 models annual rate with `sqrt(exposure_clean)` training weights and multiplies predicted rate by exposure exactly once. Preprocessing is fitted only on the fold training rows. IDs, outcome fields, contacts, renewal decision, current monetary history, weather and telematics score are excluded.

S6 retains motor age nonlinearity/missingness, buildings log-sum-insured/occupancy-security, and contents log-sum-insured/household-use/security-value blocks. Sum-insured adoption remains a human decision. Motor vehicle/mileage and buildings construction interaction did not improve the primary fold and were rejected.

## Validation and limitations

F2023 is the main fold; F2024 is the frozen recent-year challenge. S5 B3 pooled D² was 0.108781/0.085145; S6 selected D² was 0.113452/0.089801. F2024 S6 A/E was 0.908890, driven particularly by returning policies (0.897049 versus 1.021134 for new policies). The selected S6 candidate also beats S5 after a separate fixed-prediction sensitivity removes the largest linked claim amount from each fold, but those adjusted scores are not alternative targets. These comparisons do not establish ultimate accuracy because historical financial valuations, monetary IBNR, future recoveries and final financial basis are unavailable. Human actuarial approval is pending. No LightGBM, ensemble or submitted prediction exists.
