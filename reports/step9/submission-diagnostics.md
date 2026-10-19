# Step 9 submission diagnostics

These are snapshot-proxy predictions, not validated ultimate outcomes. No 2025 labels exist. All totals are CU; exposure uses the inherited ACT/365 candidate. No total was forced, clipped or recalibrated.

## 2025 predictions

| Line | Rows | Exposure | Total CU | Cost/exposure | Small <1 count/total | Large >10000 count/total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| motor | 254986 | 199983.6004 | 106408103.15 | 532.084146 | 41 / 36.56 | 0 / 0.00 |
| buildings | 184155 | 150243.9088 | 65758748.40 | 437.679963 | 38 / 30.41 | 0 / 0.00 |
| contents | 187498 | 150123.7728 | 17387149.91 | 115.818765 | 716 / 433.24 | 0 / 0.00 |

Overall: 626,639 rows, 500351.2820 exposure, 189554001.46 CU, 378.841842 CU/exposure. Quantiles below are row costs, not rates.

## Full distribution

```json
{
  "motor": {
    "rows": 254986,
    "exposure": 199983.6004,
    "prediction_total": 106408103.14559814,
    "cost_per_exposure": 532.0841455637586,
    "quantiles": {
      "0": 0.6687265705079244,
      "0.01": 9.278276900807825,
      "0.05": 47.05149281689394,
      "0.5": 402.86844556128676,
      "0.9": 715.8941773812348,
      "0.95": 831.2940405333475,
      "0.99": 1117.602582434602,
      "0.999": 1670.2536042951751,
      "1": 4475.710575972852
    },
    "small_count": 41,
    "small_total": 36.5573615092823,
    "large_count": 0,
    "large_total": 0.0
  },
  "buildings": {
    "rows": 184155,
    "exposure": 150243.90879999998,
    "prediction_total": 65758748.39939484,
    "cost_per_exposure": 437.679962699392,
    "quantiles": {
      "0": 0.46719775247242956,
      "0.01": 10.22776772323519,
      "0.05": 50.243971298601856,
      "0.5": 357.6274293959452,
      "0.9": 586.216238083176,
      "0.95": 665.3662539186674,
      "0.99": 843.8870454334237,
      "0.999": 1104.5346199403223,
      "1": 2174.077352537493
    },
    "small_count": 38,
    "small_total": 30.408757217532408,
    "large_count": 0,
    "large_total": 0.0
  },
  "contents": {
    "rows": 187498,
    "exposure": 150123.7728,
    "prediction_total": 17387149.91093321,
    "cost_per_exposure": 115.81876465426275,
    "quantiles": {
      "0": 0.08767082341070934,
      "0.01": 2.2241122612311592,
      "0.05": 11.568006538358834,
      "0.5": 88.60450710794825,
      "0.9": 159.34402973660997,
      "0.95": 186.29164823893626,
      "0.99": 250.38011453041048,
      "0.999": 368.36047516975043,
      "1": 1046.9444351414313
    },
    "small_count": 716,
    "small_total": 433.2428475728515,
    "large_count": 0,
    "large_total": 0.0
  },
  "overall": {
    "rows": 626639,
    "exposure": 500351.282,
    "prediction_total": 189554001.45592618,
    "cost_per_exposure": 378.84184227177855
  }
}
```

## Full-training comparison (in-sample, not validation)

```json
{
  "motor": {
    "rows": 979968,
    "exposure": 787157.5563,
    "prediction_total": 425413402.96753824,
    "cost_per_exposure": 540.4425067926369,
    "quantiles": {
      "0": 0.6196206912081723,
      "0.01": 10.337000054035883,
      "0.05": 53.837395142936835,
      "0.5": 419.4556814486408,
      "0.9": 733.1976027485972,
      "0.95": 854.0435416819553,
      "0.99": 1145.7110060742132,
      "0.999": 1681.7699342101932,
      "1": 4772.844423034046
    },
    "small_count": 135,
    "small_total": 117.19388861398855,
    "large_count": 0,
    "large_total": 0.0,
    "observed_total": 428762846.58,
    "in_sample_A_over_E": 1.0078733852509045
  },
  "buildings": {
    "rows": 707726,
    "exposure": 590560.1951,
    "prediction_total": 244301398.09065598,
    "cost_per_exposure": 413.6773865182164,
    "quantiles": {
      "0": 0.4261558611391944,
      "0.01": 10.43116939620711,
      "0.05": 52.06983654201842,
      "0.5": 345.424105577344,
      "0.9": 557.2813869374895,
      "0.95": 631.2213070768355,
      "0.99": 795.7981384028874,
      "0.999": 1034.7735437163349,
      "1": 2095.221460603337
    },
    "small_count": 178,
    "small_total": 139.87954936431822,
    "large_count": 0,
    "large_total": 0.0,
    "observed_total": 246656437.26999998,
    "in_sample_A_over_E": 1.0096398923532566
  },
  "contents": {
    "rows": 721617,
    "exposure": 590859.3077,
    "prediction_total": 66032342.980423406,
    "cost_per_exposure": 111.75645728162134,
    "quantiles": {
      "0": 0.09065383173903391,
      "0.01": 2.4045468257124307,
      "0.05": 12.261681903250054,
      "0.5": 87.79555271121095,
      "0.9": 154.8654607660945,
      "0.95": 180.16414858466695,
      "0.99": 240.68564657444617,
      "0.999": 348.700188613823,
      "1": 876.6962127563079
    },
    "small_count": 2626,
    "small_total": 1594.6564599321373,
    "large_count": 0,
    "large_total": 0.0,
    "observed_total": 65737584.58,
    "in_sample_A_over_E": 0.995536151117479
  },
  "overall": {
    "rows": 2409311,
    "exposure": 1968577.0591,
    "prediction_total": 735747144.0386176,
    "cost_per_exposure": 373.7456660065869
  }
}
```

## Observed snapshot cohort rates

```json
[
  {
    "line": "buildings",
    "year": 2021,
    "rows": 155729,
    "exposure": 140782.9297,
    "observed": 54052834.19,
    "observed_per_exposure": 383.94451873663485
  },
  {
    "line": "buildings",
    "year": 2022,
    "rows": 183864,
    "exposure": 149872.4413,
    "observed": 60417182.3,
    "observed_per_exposure": 403.12402851343955
  },
  {
    "line": "buildings",
    "year": 2023,
    "rows": 184132,
    "exposure": 149987.3017,
    "observed": 64832471.23,
    "observed_per_exposure": 432.25306739417124
  },
  {
    "line": "buildings",
    "year": 2024,
    "rows": 184001,
    "exposure": 149917.5224,
    "observed": 67353949.55,
    "observed_per_exposure": 449.2733635918199
  },
  {
    "line": "contents",
    "year": 2021,
    "rows": 158848,
    "exposure": 140931.3835,
    "observed": 14861300.73,
    "observed_per_exposure": 105.45061263802893
  },
  {
    "line": "contents",
    "year": 2022,
    "rows": 187632,
    "exposure": 149986.1985,
    "observed": 15820781.87,
    "observed_per_exposure": 105.48158449392261
  },
  {
    "line": "contents",
    "year": 2023,
    "rows": 187646,
    "exposure": 149974.9574,
    "observed": 17539466.93,
    "observed_per_exposure": 116.94930429765202
  },
  {
    "line": "contents",
    "year": 2024,
    "rows": 187491,
    "exposure": 149966.7683,
    "observed": 17516035.05,
    "observed_per_exposure": 116.79944329373137
  },
  {
    "line": "motor",
    "year": 2021,
    "rows": 216008,
    "exposure": 187991.5452,
    "observed": 105897441.08,
    "observed_per_exposure": 563.3095944146747
  },
  {
    "line": "motor",
    "year": 2022,
    "rows": 254685,
    "exposure": 199698.5046,
    "observed": 114890724.91,
    "observed_per_exposure": 575.3209075858048
  },
  {
    "line": "motor",
    "year": 2023,
    "rows": 254577,
    "exposure": 199681.8647,
    "observed": 117307703.7,
    "observed_per_exposure": 587.4729979922909
  },
  {
    "line": "motor",
    "year": 2024,
    "rows": 254698,
    "exposure": 199785.6418,
    "observed": 90666976.89,
    "observed_per_exposure": 453.8212860199646
  }
]
```

## Controlled same-2025-row full-refit distribution comparison

```json
{
  "motor": {
    "fold_F2024_model_on_same_2025_rows_total": 112571975.93836647,
    "full_model_on_same_2025_rows_total": 106408103.14559814,
    "total_change_fraction": -0.05475494892390509,
    "row_ratio_min": 0.7772588747646303,
    "row_ratio_max": 1.0782918943186413,
    "ratio_quantiles": {
      "0.01": 0.8471297724877653,
      "0.5": 0.954897385331198,
      "0.99": 1.029638972177799
    }
  },
  "buildings": {
    "fold_F2024_model_on_same_2025_rows_total": 64968475.01563993,
    "full_model_on_same_2025_rows_total": 65758748.39939484,
    "total_change_fraction": 0.012163951571353193,
    "row_ratio_min": 0.9069933147792526,
    "row_ratio_max": 1.2258095902206207,
    "ratio_quantiles": {
      "0.01": 0.9543299412532916,
      "0.5": 1.0142705499676017,
      "0.99": 1.1434226152851683
    }
  },
  "contents": {
    "fold_F2024_model_on_same_2025_rows_total": 17211248.9452742,
    "full_model_on_same_2025_rows_total": 17387149.91093321,
    "total_change_fraction": 0.01022011628663999,
    "row_ratio_min": 0.8658302067365503,
    "row_ratio_max": 1.1034942720362886,
    "ratio_quantiles": {
      "0.01": 0.9174347470394077,
      "0.5": 1.015688532697173,
      "0.99": 1.0562965840420455
    }
  }
}
```

## Inherited holdout calibration — NOT test calibration

```json
{
  "F2023": {
    "metric": "Tweedie D\u00b2 score",
    "power": 1.5,
    "mean_tweedie_deviance": 103.49608782239278,
    "d2_tweedie_score": 0.11345157013436835,
    "d2_status": "defined",
    "d2_error": null,
    "pooling": "pooled_policy_period_rows",
    "weighting": "unweighted_unless_explicit_sample_weight_is_supplied",
    "competition_pooling_and_weighting_status": "unresolved",
    "prediction_sum": 190183594.93962377,
    "A_over_E": 1.0499309465855395,
    "predicted_cost_per_exposure": 380.6381099675485
  },
  "F2024": {
    "metric": "Tweedie D\u00b2 score",
    "power": 1.5,
    "mean_tweedie_deviance": 99.43930802654187,
    "d2_tweedie_score": 0.08980138282838457,
    "d2_status": "defined",
    "d2_error": null,
    "pooling": "pooled_policy_period_rows",
    "weighting": "unweighted_unless_explicit_sample_weight_is_supplied",
    "competition_pooling_and_weighting_status": "unresolved",
    "prediction_sum": 193133327.63795352,
    "A_over_E": 0.9088900586803975,
    "predicted_cost_per_exposure": 386.5218118521741
  }
}
```

## Returning/new policies and customers

```json
[
  {
    "entity": "policy_id",
    "line": "motor",
    "segment": "returning",
    "rows": 216108,
    "exposure": 181949.9577,
    "prediction_total": 95824624.76422115,
    "predicted_cost_per_exposure": 526.6537347714984
  },
  {
    "entity": "policy_id",
    "line": "motor",
    "segment": "new",
    "rows": 38878,
    "exposure": 18033.642700000004,
    "prediction_total": 10583478.381377004,
    "predicted_cost_per_exposure": 586.8741306146096
  },
  {
    "entity": "policy_id",
    "line": "buildings",
    "segment": "returning",
    "rows": 156264,
    "exposure": 136681.08490000002,
    "prediction_total": 59824393.36314155,
    "predicted_cost_per_exposure": 437.69328731119504
  },
  {
    "entity": "policy_id",
    "line": "buildings",
    "segment": "new",
    "rows": 27891,
    "exposure": 13562.8239,
    "prediction_total": 5934355.036253283,
    "predicted_cost_per_exposure": 437.5456822272302
  },
  {
    "entity": "policy_id",
    "line": "contents",
    "segment": "returning",
    "rows": 159070,
    "exposure": 136579.0921,
    "prediction_total": 15804462.044876836,
    "predicted_cost_per_exposure": 115.71655516135061
  },
  {
    "entity": "policy_id",
    "line": "contents",
    "segment": "new",
    "rows": 28428,
    "exposure": 13544.680699999999,
    "prediction_total": 1582687.8660563785,
    "predicted_cost_per_exposure": 116.84940391812843
  },
  {
    "entity": "customer_id_clean",
    "line": "motor",
    "segment": "returning",
    "rows": 216108,
    "exposure": 181949.9577,
    "prediction_total": 95824624.76422115,
    "predicted_cost_per_exposure": 526.6537347714984
  },
  {
    "entity": "customer_id_clean",
    "line": "motor",
    "segment": "new",
    "rows": 38878,
    "exposure": 18033.642700000004,
    "prediction_total": 10583478.381377004,
    "predicted_cost_per_exposure": 586.8741306146096
  },
  {
    "entity": "customer_id_clean",
    "line": "buildings",
    "segment": "returning",
    "rows": 156264,
    "exposure": 136681.08490000002,
    "prediction_total": 59824393.36314155,
    "predicted_cost_per_exposure": 437.69328731119504
  },
  {
    "entity": "customer_id_clean",
    "line": "buildings",
    "segment": "new",
    "rows": 27891,
    "exposure": 13562.8239,
    "prediction_total": 5934355.036253283,
    "predicted_cost_per_exposure": 437.5456822272302
  },
  {
    "entity": "customer_id_clean",
    "line": "contents",
    "segment": "returning",
    "rows": 159070,
    "exposure": 136579.0921,
    "prediction_total": 15804462.044876836,
    "predicted_cost_per_exposure": 115.71655516135061
  },
  {
    "entity": "customer_id_clean",
    "line": "contents",
    "segment": "new",
    "rows": 28428,
    "exposure": 13544.680699999999,
    "prediction_total": 1582687.8660563785,
    "predicted_cost_per_exposure": 116.84940391812843
  }
]
```

## Unresolved sum-insured unit sensitivity

```json
{
  "buildings": {
    "affected_test_rows": 370,
    "chosen_candidate_affected_prediction_total": 135011.54842704278,
    "interpretation": "raw-unit counterfactual only; no model/response selection, no adoption",
    "raw_unit_counterfactual_total": 7.646084629767352e+188,
    "difference_from_selected_total": 7.646084629767352e+188
  },
  "contents": {
    "affected_test_rows": 360,
    "chosen_candidate_affected_prediction_total": 34708.40106847639,
    "interpretation": "raw-unit counterfactual only; no model/response selection, no adoption",
    "raw_unit_counterfactual_total": 3.6391466452462326e+282,
    "difference_from_selected_total": 3.6391466452462326e+282
  }
}
```

## Maturity, recovery and trend sensitivity

```json
{
  "recorded_recoveries_subtracted_from_training_reference": 27501378.71,
  "already_net_incurred_interpretation_adds_to_training_reference": 27501378.71,
  "case_balance": 90168216.94,
  "illustrative_case_0p8_training_reference": 723123225.042,
  "illustrative_case_1p2_training_reference": 759190511.8180001,
  "no_refitted_predictions_for_alternative_responses": true,
  "chosen_unreported_loss_allowance": 0,
  "chosen_further_development_adjustment": 0,
  "chosen_future_recovery_adjustment": 0,
  "chosen_2025_trend_factor": 1,
  "reason": "identity snapshot proxy, not estimates that these ultimate components are zero",
  "additional_adjustment_to_final_predictions": 0,
  "ultimate_prediction_sensitivity": "not identified: no supported monetary IBNR, reserve adequacy, future recovery or trend parameters; do not invent a quantitative bound"
}
```

## Review alerts

```json
[]
```

## Interpretation and limitations

Full refitting adds the immature 2024 snapshot. Earlier monetary labels were valued at end-2024, not at historical prediction boundaries; comparisons remain retrospective proxies. F2024 was reused during development. The primary F2023 S6 A/E is 1.049931; F2024 is 0.908890, especially motor 0.803431. These are material maturity/calibration limitations, not evidence to scale 2025 totals. The 11.89m CU BI claim was retained.

Raw SI sensitivity deliberately extrapolates values believed to have a unit error; even a finite huge counterfactual is not a plausible alternative forecast. Its impact motivates human review of the 730 repaired test values, not a model change in Step 9. Recovery interpretation and case stresses quantify uncertainty in the repaired TRAINING reference only; they do not imply a matching change in model predictions without a separately authorised refit. The ultimate effect of unreported/developing claims and 2025 trend cannot be quantified from this snapshot alone. Zero added allowances mean a proxy specification, not actuarial estimates of zero uncertainty. Quarantined claims remain excluded.

No unexplained critical mechanical/distribution alert remains if the acceptance gate passes; disclosed financial uncertainties remain unresolved. No actuarial approval, official scorer equivalence, Kaggle acceptance or production readiness is claimed. Current Kaggle access failed; old deadlines and submission limits are not reverified. Human review and final Kaggle-entry selection remain pending.
