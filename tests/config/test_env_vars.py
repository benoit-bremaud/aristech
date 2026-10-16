"""Integration test: a `.env` must exist and expose the dataset paths.

Marked `integration` because it depends on the machine's file system (a filled
`.env`). Deselected by default and in CI.
"""

import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="module", autouse=True)
def _load_env():
    load_dotenv()


_REQUIRED_VARS = ["SOURCE_FOLDER", "TRAIN_FOLDER", "VALIDATION_FOLDER", "TEST_FOLDER"]


@pytest.mark.integration
@pytest.mark.parametrize("var", _REQUIRED_VARS)
def test_env_var_is_set(var: str):
    assert os.getenv(var) is not None, f"Variable {var} missing from .env"
