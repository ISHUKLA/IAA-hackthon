PYTHON ?= python

.PHONY: help check doctor step1-check step2-check step2-acceptance prepare-data repair-step2 step3-check build-targets step3-acceptance target step5-check run-baselines step5-acceptance step6-check run-feature-experiments step6-diagnostics step6-acceptance step7-check step7-preflight run-lightgbm-challenger step7-acceptance step8-check step8-preflight step8-diagnosis run-conditional-complexity step8-acceptance

DATA_DIR ?= $(IAA_DATA_DIR)
STEP2_OUTPUT ?= outputs/step2/prepared
STEP2_CONFIG ?= configs/cleaning.json
STEP3_OUTPUT ?= outputs/step3/prepared
STEP3_CONFIG ?= configs/target_construction.json
STEP2_REPAIR_OUTPUT ?= outputs/step2/repairs
SCENARIO_CONFIG ?= configs/reserving_scenarios.json
STEP5_OUTPUT ?= outputs/step5/baselines
STEP6_OUTPUT ?= outputs/step6/features

help:
	@echo "check: scaffold; step1-check/step2-check/step3-check: synthetic gates; prepare-data/build-targets: local builds; step2-acceptance/step3-acceptance: real-data reconciliation"

check:
	$(PYTHON) scripts/check_repo.py
	$(PYTHON) -m compileall -q src scripts

doctor:
	$(PYTHON) -m iaa_hackathon doctor

step1-check:
	$(PYTHON) scripts/step1_check.py

step2-check:
	PYTHONPATH=src $(PYTHON) scripts/step2_check.py

step2-acceptance:
	PYTHONPATH=src $(PYTHON) scripts/step2_acceptance.py --output-dir "$(STEP2_OUTPUT)" --config "$(STEP2_CONFIG)"

prepare-data:
	PYTHONPATH=src $(PYTHON) -m iaa_hackathon prepare-data --data-dir "$(DATA_DIR)" --output-dir "$(STEP2_OUTPUT)" --cleaning-config "$(STEP2_CONFIG)"

repair-step2:
	PYTHONPATH=src $(PYTHON) -m iaa_hackathon repair-step2 --data-dir "$(DATA_DIR)" --output-dir "$(STEP2_REPAIR_OUTPUT)"

step3-check:
	PYTHONPATH=src $(PYTHON) scripts/step3_check.py

build-targets:
	PYTHONPATH=src $(PYTHON) -m iaa_hackathon build-targets --data-dir "$(DATA_DIR)" --step2-dir "$(STEP2_OUTPUT)" --output-dir "$(STEP3_OUTPUT)" --target-config "$(STEP3_CONFIG)" --scenario-config "$(SCENARIO_CONFIG)"

target: build-targets

step3-acceptance:
	PYTHONPATH=src $(PYTHON) scripts/step3_acceptance.py --output-dir "$(STEP3_OUTPUT)" --step2-dir "$(STEP2_OUTPUT)" --data-dir "$(DATA_DIR)"

step5-check:
	PYTHONPATH=src $(PYTHON) scripts/step5_check.py

run-baselines:
	PYTHONPATH=src $(PYTHON) scripts/run_baselines.py --step2-dir "$(STEP2_REPAIR_OUTPUT)" --data-dir "$(DATA_DIR)" --config configs/baselines.json --output-dir "$(STEP5_OUTPUT)"

step5-acceptance:
	PYTHONPATH=src $(PYTHON) scripts/step5_acceptance.py --output-dir "$(STEP5_OUTPUT)" --step2-dir "$(STEP2_REPAIR_OUTPUT)"

step6-check:
	PYTHONPATH=src $(PYTHON) scripts/step6_check.py

run-feature-experiments:
	PYTHONPATH=src $(PYTHON) scripts/run_feature_experiments.py --step2-dir "$(STEP2_REPAIR_OUTPUT)" --baseline-dir "$(STEP5_OUTPUT)" --baseline-config configs/baselines.json --config configs/features.json --output-dir "$(STEP6_OUTPUT)"

step6-diagnostics:
	PYTHONPATH=src $(PYTHON) scripts/model_diagnostics.py --step2-dir "$(STEP2_REPAIR_OUTPUT)" --baseline-dir "$(STEP5_OUTPUT)" --feature-dir "$(STEP6_OUTPUT)"

step6-acceptance:
	PYTHONPATH=src $(PYTHON) scripts/step6_acceptance.py --output-dir "$(STEP6_OUTPUT)" --step2-dir "$(STEP2_REPAIR_OUTPUT)"

step8-check:
	PYTHONPATH=src $(PYTHON) -m pytest -q tests/test_complexity_preflight.py tests/test_restricted_complexity.py tests/test_baselines.py tests/test_reporting.py tests/test_validation_folds.py tests/test_validation_scoring.py

step8-preflight:
	PYTHONPATH=src $(PYTHON) -m iaa_hackathon.complexity_preflight

step8-diagnosis:
	PYTHONPATH=src $(PYTHON) scripts/step8_diagnosis.py

run-conditional-complexity:
	PYTHONPATH=src $(PYTHON) scripts/run_conditional_complexity.py

step8-acceptance:
	PYTHONPATH=src $(PYTHON) scripts/step8_acceptance.py

step7-check:
	PYTHONPATH=src $(PYTHON) -m pytest -q tests/test_lightgbm_challenger.py tests/test_reporting.py tests/test_validation_folds.py tests/test_validation_scoring.py

step7-preflight:
	PYTHONPATH=src $(PYTHON) scripts/step7_preflight.py

run-lightgbm-challenger:
	PYTHONPATH=src $(PYTHON) scripts/run_lightgbm_challenger.py

step7-acceptance:
	PYTHONPATH=src $(PYTHON) scripts/step7_acceptance.py

.PHONY: step9-check step9-preflight build-final-model build-submission verify-submission reproduce-step9 step9-finalize

step9-check:
	PYTHONPATH=src $(PYTHON) -m pytest -q tests/test_final_submission.py tests/test_submission.py tests/test_baselines.py tests/test_metrics.py

step9-preflight:
	PYTHONPATH=src $(PYTHON) scripts/step9.py preflight --data-dir "$(DATA_DIR)"

build-final-model:
	PYTHONPATH=src $(PYTHON) scripts/step9.py model --data-dir "$(DATA_DIR)"

build-submission:
	PYTHONPATH=src $(PYTHON) scripts/step9.py submission --data-dir "$(DATA_DIR)"

verify-submission:
	PYTHONPATH=src $(PYTHON) scripts/step9.py verify --data-dir "$(DATA_DIR)"

reproduce-step9:
	PYTHONPATH=src $(PYTHON) scripts/step9.py reproduce --data-dir "$(DATA_DIR)"

step9-finalize:
	PYTHONPATH=src $(PYTHON) scripts/step9.py finalize --data-dir "$(DATA_DIR)"
