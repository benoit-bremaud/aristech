import unittest
from src.model_training.model_architecture import create_model

class TestModelArchitecture(unittest.TestCase):
    def test_create_model(self):
        model = create_model()
        self.assertIsNotNone(model)
        self.assertEqual(len(model.layers), 9)

if __name__ == "__main__":
    unittest.main()
