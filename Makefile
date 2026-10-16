.PHONY: install install-dev lock test test-unit test-integration lint format type-check clean run train sonar

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Régénère requirements.txt à partir de requirements.in (pip-tools).
lock:
	pip-compile --strip-extras requirements.in

test:
	pytest

test-unit:
	pytest tests/unit -q

test-integration:
	pytest -m integration

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

type-check:
	mypy

# Coverage + analysis on the local SonarQube; needs SONAR_TOKEN in the environment.
sonar:
	pytest tests/unit -q --cov=aristech --cov-report=xml
	sonar-scanner

run:
	python -m aristech --config config/config.yaml

train:
	python scripts/train_model.py

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache .scannerwork coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
