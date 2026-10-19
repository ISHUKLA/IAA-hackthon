"""Step 4 framework for scoring externally supplied predictions; no training."""
from pathlib import Path
import json
import pandas as pd
from iaa_hackathon.validation_scoring import score_supplied_predictions

def evaluate_prediction_file(response_path: Path, prediction_path: Path, output_path: Path) -> dict:
    predictions=pd.read_parquet(prediction_path)
    fold=str(predictions.fold_id.iloc[0]); version=str(predictions.response_version.iloc[0])
    result=score_supplied_predictions(pd.read_parquet(response_path),predictions,fold_id=fold,response_version=version)
    result.update({'run_kind':'externally_supplied_predictions','training':'not_performed'})
    output_path.write_text(json.dumps(result,indent=2)+'\n')
    return result
