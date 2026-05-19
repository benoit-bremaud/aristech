"""Test unitaire : construction du modèle (pas d'entraînement)."""

import pytest

# Skip module entier si tensorflow indisponible (par ex. en CI lint-only).
tf = pytest.importorskip("tensorflow")

from aristech.training.model_architecture import create_model  # noqa: E402


def test_create_model_has_nine_layers():
    model = create_model()
    assert model is not None
    assert len(model.layers) == 9
