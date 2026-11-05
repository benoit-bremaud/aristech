import tomllib
from pathlib import Path

import yaml

from aristech import __version__

ROOT = Path(__file__).resolve().parents[2]


def test_config_yaml_has_expected_sections():
    config = yaml.safe_load((ROOT / "config" / "config.yaml").read_text())
    # No `app` section: the running version is the package's (`aristech.__version__`).
    assert set(config) == {"alert", "health"}


def test_package_version_matches_pyproject():
    # Two copies of the version (pyproject.toml, aristech.__version__): they must not drift.
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert __version__ == pyproject["project"]["version"]


def test_logging_yaml_has_expected_sections():
    logging_config = yaml.safe_load((ROOT / "config" / "logging.yaml").read_text())
    assert "formatters" in logging_config
    assert "handlers" in logging_config
    assert "loggers" in logging_config
