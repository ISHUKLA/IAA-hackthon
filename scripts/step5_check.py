"""Raw-data-free Step 5 gate."""
import json, subprocess, sys
tests=['tests/test_baselines.py','tests/test_validation_scoring.py','tests/test_validation_runner.py']
r=subprocess.run([sys.executable,'-m','pytest','-q',*tests]);
if r.returncode: raise SystemExit(r.returncode)
print(json.dumps({'status':'passed','tests_collected':7,'raw_data_required':False,'scope':'S5 arithmetic, exposure equivalence, train-only pipeline and scoring alignment'},indent=2))
