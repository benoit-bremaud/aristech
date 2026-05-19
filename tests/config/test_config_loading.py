from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_config_yaml_has_expected_sections():
    config = yaml.safe_load((ROOT / "config" / "config.yaml").read_text())
    assert config["app"]["name"] == "Aristech"
    assert "video_source" in config
    assert "sound_detection" in config
    assert "hornet_detection" in config


def test_logging_yaml_has_expected_sections():
    logging_config = yaml.safe_load((ROOT / "config" / "logging.yaml").read_text())
    assert "formatters" in logging_config
    assert "handlers" in logging_config
    assert "loggers" in logging_config
