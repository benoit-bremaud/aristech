"""Test d'intégration : enchaîne préparation + entraînement + évaluation."""

import pytest

tf = pytest.importorskip("tensorflow")


@pytest.mark.integration
def test_evaluate_model_after_one_step():
    from aristech.training.data_preparation import prepare_data
    from aristech.training.evaluate import evaluate_model
    from aristech.training.model_architecture import create_model
    from aristech.training.train import compile_model, train_model

    train_generator, validation_generator, test_generator = prepare_data()
    model = compile_model(create_model())
    train_model(
        model,
        train_generator,
        validation_generator,
        epochs=1,
        steps_per_epoch=1,
        validation_steps=1,
    )
    _, test_acc = evaluate_model(model, test_generator, steps=1)
    assert test_acc >= 0.0
