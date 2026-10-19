PYTHON ?= python

.PHONY: help check doctor step1-check step2-check step2-acceptance prepare-data repair-step2 step3-check build-targets step3-acceptance target

DATA_DIR ?= $(IAA_DATA_DIR)
STEP2_OUTPUT ?= outputs/step2/prepared
STEP2_CONFIG ?= configs/cleaning.json
STEP3_OUTPUT ?= outputs/step3/prepared
STEP3_CONFIG ?= configs/target_construction.json
STEP2_REPAIR_OUTPUT ?= outputs/step2/repairs
SCENARIO_CONFIG ?= configs/reserving_scenarios.json

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
