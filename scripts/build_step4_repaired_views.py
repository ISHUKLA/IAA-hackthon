"""Persist repaired-universe fold response views and fold-safe reporting fits."""
from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
from iaa_hackathon.reporting import fit_reporting_groups

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

ap=argparse.ArgumentParser(); ap.add_argument('--step2-dir',type=Path,required=True); ap.add_argument('--config',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); args=ap.parse_args()
config=json.loads(args.config.read_text()); policy=args.step2_dir/'model/training-model-table.parquet'; claims_path=args.step2_dir/'claims/matched.parquet'; audit=args.step2_dir/'repair-audit.json'
for p in (policy,claims_path,audit):
    if not p.is_file(): raise FileNotFoundError(p)
args.output_dir.mkdir(parents=True,exist_ok=True); response_dir=args.output_dir/'responses'; response_dir.mkdir(exist_ok=True); reporting_dir=args.output_dir/'reporting'; reporting_dir.mkdir(exist_ok=True)
columns=['row_id','period_start','line','exposure_clean','observed_net_incurred']; pieces=[]
for batch in pq.ParquetFile(policy).iter_batches(batch_size=150000,columns=columns):
    part=batch.to_pandas(); part['period_year']=pd.to_datetime(part.period_start).dt.year; pieces.append(part)
frame=pd.concat(pieces,ignore_index=True); row_year=frame.set_index('row_id')['period_year']
claims=pd.read_parquet(claims_path); claims['loss_row_year']=claims.matched_row_id.map(row_year)
manifest={'status':'complete','experiment_mode':config['experiment_mode'],'financial_valuation_date':config['financial_valuation_date'],'claim_universe':config['input_universe']['claim_universe'],'inputs':{'policy':sha(policy),'matched_claims':sha(claims_path),'repair_audit':sha(audit)},'folds':{}}
for fold in config['folds']:
    selected=frame[frame.period_year.isin(fold['train_years']+[fold['validation_year']])].copy(); selected['role']='train'; selected.loc[selected.period_year.eq(fold['validation_year']),'role']='validation'
    out=selected[['row_id','line','period_year','role','exposure_clean','observed_net_incurred']].rename(columns={'observed_net_incurred':'observed_net_baseline'}); path=response_dir/f"{fold['id']}.parquet"; out.to_parquet(path,index=False)
    cutoff=pd.Timestamp(fold['prediction_boundary']); fit_claims=claims[claims.loss_row_year.isin(fold['train_years']) & (pd.to_datetime(claims.report_date)<=cutoff)].copy()
    fits=fit_reporting_groups(fit_claims,cutoff=cutoff,min_claims=30,estimation_scope='fold_training_visible_repaired_claims')
    fit_rows=[v.to_dict() for _,v in sorted(fits.items())]; fit_path=reporting_dir/f"{fold['id']}-fits.json"; fit_path.write_text(json.dumps(fit_rows,indent=2)+'\n')
    manifest['folds'][fold['id']]={'train_years':fold['train_years'],'validation_year':fold['validation_year'],'prediction_boundary':fold['prediction_boundary'],'response_rows':len(out),'train_rows':int(out.role.eq('train').sum()),'validation_rows':int(out.role.eq('validation').sum()),'visible_training_claims':len(fit_claims),'reporting_groups':len(fits),'response_sha256':sha(path),'reporting_sha256':sha(fit_path)}
(args.output_dir/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print(json.dumps(manifest,indent=2))
