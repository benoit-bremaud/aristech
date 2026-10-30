.PHONY: install install-dev lock test test-unit test-integration lint format type-check clean run sonar m3-report prefield-train prefield-report

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	mise install
	mise x -- lefthook install

# Regenerate requirements.txt from requirements.in, for the lowest supported Python (ADR-0026).
lock:
	uv pip compile -p 3.11 --strip-extras requirements.in -o requirements.txt

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

# Pre-field model (ADR-0024): needs the `train` extra, a GPU and the image store.
prefield-train:
	@[ -n "$$STORE" ] || { echo "usage: make prefield-train STORE=… [EPOCHS=40] [PYTHON=…]"; exit 2; }
	$(PYTHON) scripts/train_rfdetr.py --store "$$STORE" --output data/runs/prefield-small \
		--epochs $${EPOCHS:-40}

prefield-report:
	@[ -n "$$VESPAI_WEIGHTS" ] && [ -n "$$YOLOV5_DIR" ] || \
		{ echo "usage: make prefield-report VESPAI_WEIGHTS=… YOLOV5_DIR=… [PYTHON=…]"; exit 2; }
	$(PYTHON) scripts/prefield_report.py \
		--rfdetr-weights data/runs/prefield-small/checkpoint_best_total.pth \
		--vespai-weights "$$VESPAI_WEIGHTS" --yolov5-dir "$$YOLOV5_DIR" \
		--out docs/research/prefield-model-test-v1-tables.md

run:
	python -m aristech --config config/config.yaml

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache .scannerwork coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
