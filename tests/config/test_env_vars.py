"""Test d'intégration : un .env doit exister et exposer les chemins data.

Marqué `integration` car dépend du système de fichiers de la machine
(présence d'un `.env` peuplé). Ne s'exécute pas en CI par défaut.
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
    assert os.getenv(var) is not None, f"Variable {var} absente du .env"
