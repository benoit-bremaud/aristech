"""Test unitaire : la sérialisation Keras crée bien un fichier sur disque."""

import pytest

tf = pytest.importorskip("tensorflow")

from aristech.training.model_architecture import create_model  # noqa: E402
from aristech.training.save_model import save_model  # noqa: E402


def test_save_model_creates_file(tmp_path):
    target = tmp_path / "test_model.keras"
    save_model(create_model(), filepath=str(target))
    assert target.exists()
