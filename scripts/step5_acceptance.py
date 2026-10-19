"""Real-data S5 output acceptance."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np, pandas as pd
ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',type=Path,required=True); ap.add_argument('--step2-dir',type=Path,required=True); a=ap.parse_args()
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
m=json.loads((a.output_dir/'manifest.json').read_text()); results=json.loads((a.output_dir/'results.json').read_text()); errors=[]
if m['status']!='complete' or m['inputs']['training_model_table']!=sha(a.step2_dir/'model/training-model-table.parquet'): errors.append('upstream identity mismatch')
for fold,count in [('F2023',626355),('F2024',626190)]:
 for model in ['B0_global_mean','B1_line_exposure_rate','B2_line_premium_ratio','B3_compact_tweedie_glm']:
  p=a.output_dir/'predictions'/f'{fold}-{model}.parquet'; d=pd.read_parquet(p)
  if len(d)!=count or d.row_id.duplicated().any() or not np.isfinite(d.prediction).all() or (d.prediction<=0).any(): errors.append(f'invalid {fold}/{model}')
if not all(x.get('converged',True) for x in results if x['model_id']=='B3_compact_tweedie_glm'): errors.append('a GLM did not converge')
if not m['pipeline_check']['exact_id_coverage'] or m['pipeline_check']['rows']!=626639: errors.append('pipeline CSV invalid')
if errors: raise SystemExit('; '.join(errors))
print(json.dumps({'status':'passed','F2023_rows':626355,'F2024_rows':626190,'pipeline_rows':626639,'all_glms_converged':True},indent=2))
