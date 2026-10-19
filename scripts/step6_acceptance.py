"""Real-data S6 output acceptance."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np, pandas as pd
ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',type=Path,required=True); ap.add_argument('--step2-dir',type=Path,required=True); a=ap.parse_args()
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
m=json.loads((a.output_dir/'manifest.json').read_text()); errors=[]
if m['status']!='complete' or m['input_sha256']!=sha(a.step2_dir/'model/training-model-table.parquet'): errors.append('upstream identity mismatch')
diagnostics_path=a.output_dir/'diagnostics.json'
if not diagnostics_path.exists():
 errors.append('aggregate diagnostics missing')
else:
 diagnostics=json.loads(diagnostics_path.read_text())
 if diagnostics.get('status')!='complete': errors.append('aggregate diagnostics incomplete')
 expected_inputs={'training_model_table_sha256':sha(a.step2_dir/'model/training-model-table.parquet'),'matched_claims_sha256':sha(a.step2_dir/'claims/matched.parquet')}
 if diagnostics.get('inputs')!=expected_inputs: errors.append('diagnostic input identity mismatch')
for fold,count in [('F2023',626355),('F2024',626190)]:
 d=pd.read_parquet(a.output_dir/'predictions'/f'{fold}-selected.parquet')
 if len(d)!=count or d.row_id.duplicated().any() or not np.isfinite(d.prediction).all() or (d.prediction<=0).any(): errors.append(f'invalid selected {fold}')
 if diagnostics_path.exists() and diagnostics.get('folds',{}).get(fold,{}).get('rows')!=count: errors.append(f'invalid diagnostic rows {fold}')
if errors: raise SystemExit('; '.join(errors))
print(json.dumps({'status':'passed','F2023_rows':626355,'F2024_rows':626190,'selected_blocks':m['selected_blocks']},indent=2))
