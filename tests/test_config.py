# tests/test_config.py

import yaml

def test_load_config():
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        assert isinstance(config, dict), "Configuration should be a dictionary"
    except Exception as e:
        assert False, f"Failed to load configuration: {e}"