"""Tests de la pipeline d'entraînement.

`compile_model` est testable sans données → test unitaire.
`train_model` exige des images → test d'intégration.
"""

import pytest

tf = pytest.importorskip("tensorflow")

from aristech.training.model_architecture import create_model  # noqa: E402
from aristech.training.train import compile_model, train_model  # noqa: E402


def test_compile_model_attaches_optimizer():
    model = compile_model(create_model())
    assert model.optimizer is not None


@pytest.mark.integration
def test_train_model_runs_one_step():
    from aristech.training.data_preparation import prepare_data

    train_generator, validation_generator, _ = prepare_data()
    model = compile_model(create_model())
    history = train_model(
        model,
        train_generator,
        validation_generator,
        epochs=1,
        steps_per_epoch=1,
        validation_steps=1,
    )
    assert "accuracy" in history.history
