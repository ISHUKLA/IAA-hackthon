"""Strict supplied-prediction alignment for Step 4; no estimator fitting."""
import pandas as pd
from iaa_hackathon.metrics import metric_report


def score_supplied_predictions(response: pd.DataFrame, predictions: pd.DataFrame, *, fold_id: str, response_version: str) -> dict:
    required={"row_id","observed_net_baseline"}
    if required-set(response): raise ValueError("response columns missing")
    needed={"row_id","fold_id","response_version","run_id","prediction_unit","prediction"}
    if needed-set(predictions): raise ValueError("prediction metadata or value missing")
    if predictions.row_id.isna().any() or predictions.row_id.duplicated().any(): raise ValueError("prediction row_id must be unique")
    if not predictions.fold_id.eq(fold_id).all() or not predictions.response_version.eq(response_version).all(): raise ValueError("prediction metadata mismatch")
    joined=response.merge(predictions,on="row_id",how="outer",validate="one_to_one",indicator=True)
    if not joined._merge.eq("both").all(): raise ValueError("prediction IDs do not exactly match response IDs")
    report=metric_report(joined.observed_net_baseline,joined.prediction)
    report.update({"fold_id":fold_id,"response_version":response_version,"rows":len(joined),"reference_sum":float(joined.observed_net_baseline.sum()),"prediction_sum":float(joined.prediction.sum()),"reference_A_over_E":float(joined.observed_net_baseline.sum()/joined.prediction.sum())})
    return report
