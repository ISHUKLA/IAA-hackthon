PYTHON ?= python

.PHONY: help check doctor step1-check

help:
	@echo "check: scaffold checks; doctor: local input presence; step1-check: contract and synthetic behavior"

check:
	$(PYTHON) scripts/check_repo.py
	$(PYTHON) -m compileall -q src scripts

doctor:
	$(PYTHON) -m iaa_hackathon doctor

step1-check:
	$(PYTHON) scripts/step1_check.py
