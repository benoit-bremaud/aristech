import os
from dotenv import load_dotenv
import unittest

class TestEnvVars(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_env_vars_loaded(self):
        self.assertIsNotNone(os.getenv('SOURCE_FOLDER'))
        self.assertIsNotNone(os.getenv('TRAIN_FOLDER'))
        self.assertIsNotNone(os.getenv('VALIDATION_FOLDER'))
        self.assertIsNotNone(os.getenv('TEST_FOLDER'))

if __name__ == '__main__':
    unittest.main()
