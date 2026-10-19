import numpy as np
import pandas as pd
import pytest

from iaa_hackathon.baselines import add_feature_blocks, fit_compact_glm, simple_baseline_predictions
from iaa_hackathon.metrics import mean_tweedie_deviance_15


def tiny():
    return pd.DataFrame({"row_id":[f"r{i}" for i in range(8)],"line":["motor"]*8,"exposure_clean":[.5,1,.5,1,.5,1,.5,1],"observed_net_incurred":[0,2,0,4,1,3,0,5],"written_premium":[1,2,1,2,1,2,1,2],"driver_age":[20,30,40,50,25,35,45,55],"years_licensed":[2,10,20,30,5,15,25,35],"vehicle_age":[1,2,3,4,1,2,3,4],"annual_mileage":[1000,2000,None,4000,1000,2000,3000,4000],"voluntary_excess":[100]*8,"compulsory_excess":[200]*8,"cover_type":["a","b"]*4,"vehicle_use":["p"]*8,"body_type":["x"]*8,"engine_size_cc":[1000]*8})


def test_baseline_arithmetic_and_exposure():
    data=tiny(); out=simple_baseline_predictions(data.iloc[:6],data.iloc[6:])
    assert np.all(out["B0_global_mean"] == data.iloc[:6].observed_net_incurred.mean())
    assert out["B1_line_exposure_rate"][1] == pytest.approx(2*out["B1_line_exposure_rate"][0])


def test_rate_period_deviance_identity():
    y=np.array([0.,4.]); e=np.array([.5,1.]); r=np.array([2.,3.])
    left=mean_tweedie_deviance_15(y,e*r)
    right=mean_tweedie_deviance_15(y/e,r,sample_weight=np.sqrt(e))
    assert left == pytest.approx(right*np.sqrt(e).sum()/len(e))


def test_feature_derivation_does_not_use_response():
    data=tiny(); altered=data.copy(); altered.observed_net_incurred += 1000
    a,f=add_feature_blocks(data,"motor",["age_nonlinearity","ordinary_missingness"]); b,_=add_feature_blocks(altered,"motor",["age_nonlinearity","ordinary_missingness"])
    pd.testing.assert_frame_equal(a[f],b[f])


def test_repaired_sum_insured_is_logged_once_and_identity_is_preserved():
    data=tiny().assign(line="buildings", policyholder_age=40, sum_insured_repaired=1000.0, days_unoccupied=0, construction_type_standardized="brick", occupancy="owner")
    result,features=add_feature_blocks(data,"buildings",["log_sum_insured"])
    assert result["row_id"].tolist()==data["row_id"].tolist()
    assert result["log_sum_insured"].iloc[0]==pytest.approx(np.log1p(1000.0))


def test_glm_handles_unseen_category():
    train=tiny().iloc[:6].copy(); valid=tiny().iloc[6:].copy(); valid["cover_type"]="unseen"
    prediction,_,meta=fit_compact_glm(train,valid,line="motor",max_iter=50)
    assert np.isfinite(prediction).all() and (prediction>0).all() and meta["features"]
