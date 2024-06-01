import unittest
import yaml

class TestConfigLoading(unittest.TestCase):
    def test_config_yaml(self):
        with open('config/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        self.assertEqual(config['app']['name'], 'Aristech')
        self.assertIn('video_source', config)
        self.assertIn('sound_detection', config)
        self.assertIn('hornet_detection', config)

    def test_logging_yaml(self):
        with open('config/logging.yaml', 'r') as file:
            logging_config = yaml.safe_load(file)
        self.assertIn('formatters', logging_config)
        self.assertIn('handlers', logging_config)
        self.assertIn('loggers', logging_config)

if __name__ == '__main__':
    unittest.main()
