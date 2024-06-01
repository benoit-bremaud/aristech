import unittest
from src.model_training.evaluate import evaluate_model
from src.model_training.model_architecture import create_model
from src.model_training.data_preparation import prepare_data
from src.model_training.train import compile_model, train_model

class TestEvaluateModel(unittest.TestCase):
    def test_evaluate_model(self):
        train_generator, validation_generator, test_generator = prepare_data()
        model = create_model()
        model = compile_model(model)
        train_model(model, train_generator, validation_generator, epochs=1, steps_per_epoch=1, validation_steps=1)
        test_loss, test_acc = evaluate_model(model, test_generator, steps=1)
        self.assertGreaterEqual(test_acc, 0.0)

if __name__ == "__main__":
    unittest.main()
