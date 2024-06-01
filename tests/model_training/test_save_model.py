import unittest
import os
from src.model_training.save_model import save_model
from src.model_training.model_architecture import create_model
from src.model_training.data_preparation import prepare_data
from src.model_training.train import compile_model, train_model

class TestSaveModel(unittest.TestCase):
    def test_save_model(self):
        model = create_model()
        save_model(model, filepath='test_model.h5')
        self.assertTrue(os.path.exists('test_model.h5'))
        os.remove('test_model.h5')

if __name__ == "__main__":
    unittest.main()
