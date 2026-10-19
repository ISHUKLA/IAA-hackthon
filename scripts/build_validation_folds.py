"""Batch-build ignored Step 4 membership without materialising all policy rows."""
import argparse, json
from collections import defaultdict
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

parser=argparse.ArgumentParser()
parser.add_argument('--policy',type=Path,required=True); parser.add_argument('--response',type=Path,required=True)
parser.add_argument('--config',type=Path,required=True); parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args(); config=json.loads(args.config.read_text()); args.output_dir.mkdir(parents=True,exist_ok=True)
columns=['row_id','policy_id','customer_id','line','period_start','period_end','exposure_clean','observed_net_incurred']
writer=None; totals=defaultdict(lambda:[0,0.0,0.0]); source=pq.ParquetFile(args.policy)
for batch in source.iter_batches(batch_size=100_000,columns=columns):
    frame=batch.to_pandas(); start=pd.to_datetime(frame.period_start); end=pd.to_datetime(frame.period_end)
    if frame.row_id.isna().any() or frame.row_id.duplicated().any() or (start.dt.year!=end.dt.year).any() or (end<start).any(): raise ValueError('invalid, duplicate-within-batch, or cross-year policy period')
    frame['period_year']=start.dt.year
    for fold in config['folds']:
        mask=frame.period_year.isin(fold['train_years']+[fold['validation_year']])
        out=frame.loc[mask,['row_id','policy_id','customer_id','line','period_year','exposure_clean','observed_net_incurred']].copy()
        if out.empty: continue
        out['fold_id']=fold['id']; out['role']='train'; out.loc[out.period_year.eq(fold['validation_year']),'role']='validation'; out['input_identity']=config['input_universe']['policy_bundle']
        for key,g in out.groupby(['fold_id','role','line','period_year']):
            totals[key][0]+=len(g); totals[key][1]+=float(g.exposure_clean.sum()); totals[key][2]+=float(g.observed_net_incurred.sum())
        table=pa.Table.from_pandas(out[['fold_id','row_id','line','role','period_year','input_identity']],preserve_index=False)
        if writer is None: writer=pq.ParquetWriter(args.output_dir/'fold-membership.parquet',table.schema)
        writer.write_table(table)
if writer is None: raise ValueError('no fold rows selected')
writer.close()
summary={'input_policy':str(args.policy),'response_view':str(args.response),'response_version':config['input_universe']['response_version'],'by_fold_role_line_year':[{'fold_id':k[0],'role':k[1],'line':k[2],'period_year':int(k[3]),'rows':v[0],'exposure':v[1],'observed_net':v[2]} for k,v in sorted(totals.items())]}
(args.output_dir/'fold-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'status':'complete','rows':sum(x[0] for x in totals.values()),'groups':len(totals)},indent=2))
