.PHONY: install install-dev lock test test-unit test-integration lint format type-check clean run sonar m3-report

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Regenerate requirements.txt from requirements.in (pip-tools).
lock:
	pip-compile --strip-extras requirements.in

test:
	pytest

test-unit:
	pytest tests/unit -q

# The default addopts deselect integration/e2e; a later -m overrides it.
test-integration:
	pytest -m integration

lint:
	ruff check src tests
	ruff format --check src tests

format:
	ruff format src tests
	ruff check --fix src tests

type-check:
	mypy

# Coverage + analysis on the local SonarQube. Token: the project token file
# (~/.config/sonar-tokens/aristech) when present, else SONAR_TOKEN from the environment.
SONAR_TOKEN_FILE ?= $(HOME)/.config/sonar-tokens/aristech

sonar:
	pytest -q --cov=aristech --cov-report=xml
	SONAR_TOKEN="$$(cat $(SONAR_TOKEN_FILE) 2>/dev/null || printf '%s' "$$SONAR_TOKEN")" sonar-scanner

# M3 baseline: recompute VespAI per-class P/R (docs/research/m3-vespai-baseline.md).
# Needs the vision environment (PYTHON) and three operator-supplied paths (never committed).
PYTHON ?= python
m3-report: export WEIGHTS := $(WEIGHTS)
m3-report: export YOLOV5_DIR := $(YOLOV5_DIR)
m3-report: export DATASET := $(DATASET)
m3-report:
	@[ -n "$$WEIGHTS" ] && [ -n "$$YOLOV5_DIR" ] && [ -n "$$DATASET" ] || \
		{ echo "usage: make m3-report WEIGHTS=… YOLOV5_DIR=… DATASET=… [PYTHON=…]"; exit 2; }
	$(PYTHON) scripts/vespai_baseline_report.py --weights "$$WEIGHTS" \
		--yolov5-dir "$$YOLOV5_DIR" --dataset "$$DATASET"

run:
	python -m aristech --config config/config.yaml

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache .scannerwork coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
