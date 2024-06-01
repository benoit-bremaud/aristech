import unittest
from src.model_training.data_preparation import prepare_data

class TestDataPreparation(unittest.TestCase):
    def test_prepare_data(self):
        train_generator, validation_generator, test_generator = prepare_data()
        self.assertIsNotNone(train_generator)
        self.assertIsNotNone(validation_generator)
        self.assertIsNotNone(test_generator)

if __name__ == "__main__":
    unittest.main()
