"""Run bounded S6 one-block ablations and one frozen combined candidate."""
from __future__ import annotations

import argparse, hashlib, json, platform, time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from iaa_hackathon.baselines import BASE_FEATURES, fit_compact_glm, score_vector

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

ap=argparse.ArgumentParser(); ap.add_argument('--step2-dir',type=Path,required=True); ap.add_argument('--baseline-dir',type=Path,required=True); ap.add_argument('--baseline-config',type=Path,default=Path('configs/baselines.json')); ap.add_argument('--config',type=Path,default=Path('configs/features.json')); ap.add_argument('--output-dir',type=Path,required=True); args=ap.parse_args()
cfg=json.loads(args.config.read_text()); base_cfg=json.loads(args.baseline_config.read_text()); baseline_results=json.loads((args.baseline_dir/'results.json').read_text()); train_path=args.step2_dir/'model/training-model-table.parquet'
source_columns=set(sum(BASE_FEATURES.values(),[]))
for blocks in cfg['blocks'].values():
    for block in blocks.values(): source_columns.update(block['source'])
columns=['row_id','period_start','line','exposure_clean','observed_net_incurred',*sorted(source_columns)]; data=pd.read_parquet(train_path,columns=columns); data['period_year']=pd.to_datetime(data.period_start).dt.year
args.output_dir.mkdir(parents=True,exist_ok=True); (args.output_dir/'predictions').mkdir(exist_ok=True); (args.output_dir/'models').mkdir(exist_ok=True)
start_all=time.perf_counter(); results=[]; selected={}; main_predictions=np.empty(int(data.period_year.eq(2023).sum()))
main_valid_all=data[data.period_year.eq(2023)].copy()
for line,blocks in cfg['blocks'].items():
    train=data[data.period_year.isin([2021,2022]) & data.line.eq(line)]; valid=data[data.period_year.eq(2023) & data.line.eq(line)]
    baseline=next(x for x in baseline_results if x['fold_id']=='F2023' and x['model_id']=='B3_compact_tweedie_glm' and x['scope']==line)
    improving=[]; block_rows=[]
    for block in blocks:
        pred,model,meta=fit_compact_glm(train,valid,line=line,blocks=[block],alpha=base_cfg['glm']['alpha'],max_iter=base_cfg['glm']['max_iter']); score=score_vector(valid.observed_net_incurred.to_numpy(float),pred); delta=score['mean_tweedie_deviance']-baseline['mean_tweedie_deviance']; decision='retain_candidate' if delta<0 else 'reject_no_improvement';
        if delta<0: improving.append(block)
        row={'stage':'S6','fold_id':'F2023','line':line,'candidate':block,'blocks':[block],'baseline_mean_deviance':baseline['mean_tweedie_deviance'],'delta_mean_deviance':delta,'decision':decision,**score,**meta}; results.append(row); block_rows.append((block,delta,pred,model,meta))
        pd.DataFrame({'row_id':valid.row_id,'fold_id':'F2023','response_version':base_cfg['response_version'],'run_id':f'F2023-{line}-{block}','prediction_unit':'policy_period_cost','prediction':pred}).to_parquet(args.output_dir/'predictions'/f'F2023-{line}-{block}.parquet',index=False); joblib.dump(model,args.output_dir/'models'/f'F2023-{line}-{block}.joblib')
    candidate_blocks=improving
    if candidate_blocks:
        pred,model,meta=fit_compact_glm(train,valid,line=line,blocks=candidate_blocks,alpha=base_cfg['glm']['alpha'],max_iter=base_cfg['glm']['max_iter']); score=score_vector(valid.observed_net_incurred.to_numpy(float),pred); delta=score['mean_tweedie_deviance']-baseline['mean_tweedie_deviance']
        if delta>=0:
            best=min(block_rows,key=lambda x:x[1]); candidate_blocks=[best[0]]; pred,model,meta=best[2],best[3],best[4]; score=score_vector(valid.observed_net_incurred.to_numpy(float),pred); delta=best[1]
    else:
        candidate_blocks=[]; base_pred=pd.read_parquet(args.baseline_dir/'predictions'/'F2023-B3_compact_tweedie_glm.parquet').set_index('row_id').loc[valid.row_id,'prediction'].to_numpy(); pred=base_pred; model=None; meta={'runtime_seconds':0.0,'iterations':None,'converged':True,'features':BASE_FEATURES[line],'blocks':[]}; score=score_vector(valid.observed_net_incurred.to_numpy(float),pred); delta=0.0
    selected[line]=candidate_blocks; results.append({'stage':'S6','fold_id':'F2023','line':line,'candidate':'selected_combined','blocks':candidate_blocks,'baseline_mean_deviance':baseline['mean_tweedie_deviance'],'delta_mean_deviance':delta,'decision':'freeze_for_F2024' if candidate_blocks else 'retain_S5_baseline',**score,**meta})
    main_predictions[main_valid_all.line.eq(line).to_numpy()]=pred
    if model is not None: joblib.dump(model,args.output_dir/'models'/f'F2023-{line}-selected.joblib')
pd.DataFrame({'row_id':main_valid_all.row_id,'fold_id':'F2023','response_version':base_cfg['response_version'],'run_id':'F2023-S6-selected','prediction_unit':'policy_period_cost','prediction':main_predictions}).to_parquet(args.output_dir/'predictions'/'F2023-selected.parquet',index=False)
results.append({'stage':'S6','fold_id':'F2023','line':'pooled','candidate':'selected_combined',**score_vector(main_valid_all.observed_net_incurred.to_numpy(float),main_predictions)})

# Frozen recent-year challenge.
challenge=data[data.period_year.eq(2024)].copy(); challenge_pred=np.empty(len(challenge))
for line,blocks in selected.items():
    train=data[data.period_year.isin([2021,2022,2023]) & data.line.eq(line)]; valid=challenge[challenge.line.eq(line)]; pred,model,meta=fit_compact_glm(train,valid,line=line,blocks=blocks,alpha=base_cfg['glm']['alpha'],max_iter=base_cfg['glm']['max_iter']); challenge_pred[challenge.line.eq(line).to_numpy()]=pred; baseline=next(x for x in baseline_results if x['fold_id']=='F2024' and x['model_id']=='B3_compact_tweedie_glm' and x['scope']==line); score=score_vector(valid.observed_net_incurred.to_numpy(float),pred); results.append({'stage':'S6','fold_id':'F2024','line':line,'candidate':'frozen_selected','blocks':blocks,'baseline_mean_deviance':baseline['mean_tweedie_deviance'],'delta_mean_deviance':score['mean_tweedie_deviance']-baseline['mean_tweedie_deviance'],'decision':'challenge_only',**score,**meta}); joblib.dump(model,args.output_dir/'models'/f'F2024-{line}-selected.joblib')
pd.DataFrame({'row_id':challenge.row_id,'fold_id':'F2024','response_version':base_cfg['response_version'],'run_id':'F2024-S6-selected','prediction_unit':'policy_period_cost','prediction':challenge_pred}).to_parquet(args.output_dir/'predictions'/'F2024-selected.parquet',index=False); results.append({'stage':'S6','fold_id':'F2024','line':'pooled','candidate':'frozen_selected',**score_vector(challenge.observed_net_incurred.to_numpy(float),challenge_pred)})
manifest={'status':'complete','config_id':cfg['config_id'],'baseline_config_id':base_cfg['config_id'],'input_sha256':sha(train_path),'config_sha256':sha(args.config),'code_sha256':{'baselines.py':sha(Path('src/iaa_hackathon/baselines.py')),'run_feature_experiments.py':sha(Path(__file__))},'selected_blocks':selected,'runtime_seconds':time.perf_counter()-start_all,'response_version':base_cfg['response_version'],'experiment_mode':base_cfg['experiment_mode'],'conditional_unavailable':['telematics score timing','whole-year weather','monetary history','current-status history','repaired scenario sensitivity']}
(args.output_dir/'results.json').write_text(json.dumps(results,indent=2)+'\n'); (args.output_dir/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print(json.dumps(manifest,indent=2))
