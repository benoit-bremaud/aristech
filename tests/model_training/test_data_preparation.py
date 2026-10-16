"""Test d'intégration : nécessite TRAIN/VALIDATION/TEST_FOLDER peuplés."""

import pytest

pytest.importorskip("tensorflow")

from aristech.training.data_preparation import prepare_data


@pytest.mark.integration
def test_prepare_data():
    train_generator, validation_generator, test_generator = prepare_data()
    assert train_generator is not None
    assert validation_generator is not None
    assert test_generator is not None
