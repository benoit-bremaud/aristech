import os
import shutil
import unittest
from pathlib import Path
from scripts.distribute_images import distribute_images

class TestImageDistribution(unittest.TestCase):
    def setUp(self):
        self.source_folder = 'test_data/source'
        self.train_folder = 'test_data/train'
        self.validation_folder = 'test_data/validation'
        self.test_folder = 'test_data/test'

        # Setup test directories
        os.makedirs(self.source_folder, exist_ok=True)
        os.makedirs(self.train_folder, exist_ok=True)
        os.makedirs(self.validation_folder, exist_ok=True)
        os.makedirs(self.test_folder, exist_ok=True)

        # Create dummy images
        for i in range(10):
            Path(f'{self.source_folder}/image_{i}.jpg').touch()

    def tearDown(self):
        shutil.rmtree('test_data')

    def test_image_distribution(self):
        distribute_images(self.source_folder, self.train_folder, self.validation_folder, self.test_folder)
        
        train_images = os.listdir(self.train_folder)
        validation_images = os.listdir(self.validation_folder)
        test_images = os.listdir(self.test_folder)

        self.assertEqual(len(train_images), 7)
        self.assertEqual(len(validation_images), 2)
        self.assertEqual(len(test_images), 1)

if __name__ == '__main__':
    unittest.main()
