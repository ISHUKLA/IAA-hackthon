"""Run S5 B0-B3 on frozen folds and write an ignored pipeline-check CSV."""
from __future__ import annotations

import argparse, hashlib, json, platform, time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from iaa_hackathon.baselines import BASE_FEATURES, fit_compact_glm, score_vector, simple_baseline_predictions
from iaa_hackathon.submission import SubmissionRules, order_like_sample, validate_submission_csv

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

ap=argparse.ArgumentParser(); ap.add_argument('--step2-dir',type=Path,required=True); ap.add_argument('--data-dir',type=Path,required=True); ap.add_argument('--config',type=Path,default=Path('configs/baselines.json')); ap.add_argument('--output-dir',type=Path,required=True); args=ap.parse_args()
cfg=json.loads(args.config.read_text()); train_path=args.step2_dir/'model/training-model-table.parquet'; test_path=args.step2_dir/'model/test-model-table.parquet'; audit_path=args.step2_dir/'repair-audit.json'
feature_columns=sorted(set(sum(BASE_FEATURES.values(),[]))); columns=['row_id','period_start','line','exposure_clean','observed_net_incurred','written_premium',*feature_columns]
start_all=time.perf_counter(); data=pd.read_parquet(train_path,columns=columns); data['period_year']=pd.to_datetime(data.period_start).dt.year
args.output_dir.mkdir(parents=True,exist_ok=True); (args.output_dir/'predictions').mkdir(exist_ok=True); (args.output_dir/'models').mkdir(exist_ok=True)
results=[]; fold_predictions={}
for fold_id,train_years,valid_year in [('F2023',[2021,2022],2023),('F2024',[2021,2022,2023],2024)]:
    train=data[data.period_year.isin(train_years)].copy(); valid=data[data.period_year.eq(valid_year)].copy(); simple=simple_baseline_predictions(train,valid)
    for model_id in ('B0_global_mean','B1_line_exposure_rate','B2_line_premium_ratio'):
        pred=simple[model_id]; row={'stage':'S5','fold_id':fold_id,'model_id':model_id,'response_version':cfg['response_version'],'scope':'pooled',**score_vector(valid.observed_net_incurred.to_numpy(float),pred),'runtime_seconds':0.0}
        if model_id=='B2_line_premium_ratio': row['availability']=simple['B2_status']
        results.append(row)
        for line in sorted(valid.line.unique()):
            mask=valid.line.eq(line).to_numpy(); results.append({'stage':'S5','fold_id':fold_id,'model_id':model_id,'response_version':cfg['response_version'],'scope':line,**score_vector(valid.loc[mask,'observed_net_incurred'].to_numpy(float),pred[mask]),'runtime_seconds':0.0})
        pd.DataFrame({'row_id':valid.row_id,'fold_id':fold_id,'response_version':cfg['response_version'],'run_id':f'{fold_id}-{model_id}','prediction_unit':'policy_period_cost','prediction':pred}).to_parquet(args.output_dir/'predictions'/f'{fold_id}-{model_id}.parquet',index=False)
    glm_pred=np.empty(len(valid)); line_meta={}; models={}
    for line in sorted(valid.line.unique()):
        tr=train[train.line.eq(line)]; va=valid[valid.line.eq(line)]; pred,model,meta=fit_compact_glm(tr,va,line=line,alpha=cfg['glm']['alpha'],max_iter=cfg['glm']['max_iter']); glm_pred[valid.line.eq(line).to_numpy()]=pred; line_meta[line]=meta; models[line]=model; joblib.dump(model,args.output_dir/'models'/f'{fold_id}-{line}-B3.joblib')
        results.append({'stage':'S5','fold_id':fold_id,'model_id':'B3_compact_tweedie_glm','response_version':cfg['response_version'],'scope':line,**score_vector(va.observed_net_incurred.to_numpy(float),pred),**meta})
    results.append({'stage':'S5','fold_id':fold_id,'model_id':'B3_compact_tweedie_glm','response_version':cfg['response_version'],'scope':'pooled',**score_vector(valid.observed_net_incurred.to_numpy(float),glm_pred),'runtime_seconds':sum(v['runtime_seconds'] for v in line_meta.values()),'all_lines_converged':all(v['converged'] for v in line_meta.values())})
    pd.DataFrame({'row_id':valid.row_id,'fold_id':fold_id,'response_version':cfg['response_version'],'run_id':f'{fold_id}-B3','prediction_unit':'policy_period_cost','prediction':glm_pred}).to_parquet(args.output_dir/'predictions'/f'{fold_id}-B3_compact_tweedie_glm.parquet',index=False); fold_predictions[fold_id]=glm_pred

# Exercise the 2025 file path with B1 trained on all repaired 2021-2024 rows.
test=pd.read_parquet(test_path,columns=['row_id','line','exposure_clean']); rates=data.groupby('line').apply(lambda x:x.observed_net_incurred.sum()/x.exposure_clean.sum(),include_groups=False); test['prediction']=test.line.map(rates)*test.exposure_clean
sample=pd.read_parquet(args.data_dir/'sample_submission.parquet',columns=['row_id']); candidate=order_like_sample(test[['row_id','prediction']],sample.row_id.tolist(),SubmissionRules(expected_rows=len(sample))); csv=args.output_dir/'baseline_pipeline_check.csv'; candidate.to_csv(csv,index=False); validation=validate_submission_csv(csv,sample.row_id.tolist(),SubmissionRules(expected_rows=len(sample)))
manifest={'status':'complete','config_id':cfg['config_id'],'experiment_mode':cfg['experiment_mode'],'response_version':cfg['response_version'],'inputs':{'training_model_table':sha(train_path),'test_model_table':sha(test_path),'repair_audit':sha(audit_path),'config':sha(args.config)},'code_sha256':{'baselines.py':sha(Path('src/iaa_hackathon/baselines.py')),'run_baselines.py':sha(Path(__file__))},'runtime':{'python':platform.python_version(),'pandas':pd.__version__,'total_seconds':time.perf_counter()-start_all},'rows':{'training':len(data),'test':len(test)},'pipeline_check':{**validation,'csv_sha256':sha(csv),'purpose':cfg['pipeline_check']},'limitations':cfg['pending']}
(args.output_dir/'results.json').write_text(json.dumps(results,indent=2)+'\n'); (args.output_dir/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print(json.dumps(manifest,indent=2))
