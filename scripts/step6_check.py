"""Raw-data-free Step 6 gate."""
import json, subprocess, sys
tests=['tests/test_baselines.py','tests/test_validation_folds.py','tests/test_validation_scoring.py','tests/test_validation_runner.py','tests/test_reporting.py']
r=subprocess.run([sys.executable,'-m','pytest','-q',*tests]);
if r.returncode: raise SystemExit(r.returncode)
print(json.dumps({'status':'passed','tests_collected':16,'raw_data_required':False,'scope':'S6 derived blocks, identity, reporting cutoffs, leakage guards and scoring'},indent=2))
