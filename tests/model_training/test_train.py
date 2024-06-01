import unittest
from src.model_training.train import compile_model, train_model
from src.model_training.model_architecture import create_model
from src.model_training.data_preparation import prepare_data

class TestTrainModel(unittest.TestCase):
    def test_compile_model(self):
        model = create_model()
        model = compile_model(model)
        self.assertIsNotNone(model.optimizer)

    def test_train_model(self):
        train_generator, validation_generator, _ = prepare_data()
        model = create_model()
        model = compile_model(model)
        history = train_model(model, train_generator, validation_generator, epochs=1, steps_per_epoch=1, validation_steps=1)
        self.assertIn('accuracy', history.history)

if __name__ == "__main__":
    unittest.main()
