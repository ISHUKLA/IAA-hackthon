import pandas as pd
from iaa_hackathon.validation_runner import evaluate_prediction_file
def test_synthetic_runner(tmp_path):
 r=tmp_path/'r.parquet'; p=tmp_path/'p.parquet'; o=tmp_path/'o.json'
 pd.DataFrame({'row_id':['a','b'],'observed_net_baseline':[0.,4.]}).to_parquet(r)
 pd.DataFrame({'row_id':['a','b'],'fold_id':['F2023']*2,'response_version':['v']*2,'run_id':['synthetic']*2,'prediction_unit':['cost']*2,'prediction':[1.,1.]}).to_parquet(p)
 assert evaluate_prediction_file(r,p,o)['training']=='not_performed'
