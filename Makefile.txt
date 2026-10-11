# Germany Student Companion — local and CI entry points.
# See AGENTS.md (Commands) and docs/devops-system.md (Quality gates).

PYTHON ?= python3

.PHONY: help validate lint test build evals-smoke clean

help:
	@echo "make validate     yamllint, schema checks, content, skill and adapter rules"
	@echo "make lint         ruff on scripts/ and tests/"
	@echo "make test         pytest (with coverage) and Apps Script unit tests"
	@echo "make build        packs, snapshot, per-tool skill packages, latest.json"
	@echo "make evals-smoke  10 quick eval cases on the local build"

validate:
	$(PYTHON) scripts/validate.py $(ROOT)

lint:
	ruff check scripts tests

test:
	$(PYTHON) -m pytest --cov --cov-report=term-missing
	@if [ -d node_modules ]; then npm test; else echo "skip: Apps Script tests (run npm install first)"; fi

build:
	$(PYTHON) scripts/build.py $(ROOT)

evals-smoke:
	$(PYTHON) scripts/run_evals.py --smoke

clean:
	find build -mindepth 1 ! -name README.md -delete
