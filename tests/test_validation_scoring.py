import pandas as pd
import pytest
from iaa_hackathon.validation_scoring import score_supplied_predictions
def test_alignment_and_metadata():
 r=pd.DataFrame({'row_id':['a','b'],'observed_net_baseline':[0.,4.]}); p=pd.DataFrame({'row_id':['b','a'],'fold_id':['F2023']*2,'response_version':['v']*2,'run_id':['x']*2,'prediction_unit':['cost']*2,'prediction':[1.,1.]})
 assert score_supplied_predictions(r,p,fold_id='F2023',response_version='v')['rows']==2
 p.loc[1,'row_id']='z'
 with pytest.raises(ValueError,match='exactly'): score_supplied_predictions(r,p,fold_id='F2023',response_version='v')
