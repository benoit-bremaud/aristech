"""Unit tests for the class-map parser of scripts/measure_operating_point.py."""

import importlib.util
from pathlib import Path

import pytest

from aristech.domain import Species

_SCRIPT = Path(__file__).parents[3] / "scripts" / "measure_operating_point.py"
_spec = importlib.util.spec_from_file_location("measure_operating_point", _SCRIPT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_parse_class_map_accepts_target_without_bee() -> None:
    assert _mod._parse_class_map("0:vespa_crabro,1:vespa_velutina") == {
        0: Species.VESPA_CRABRO,
        1: Species.VESPA_VELUTINA,
    }


def test_parse_class_map_rejects_missing_target() -> None:
    with pytest.raises(ValueError, match="vespa_velutina"):
        _mod._parse_class_map("0:vespa_crabro,2:apis_mellifera")


_ARGV = ["--weights", "w", "--yolov5-dir", "y", "--dataset", "/nonexistent"]


def test_main_exits_2_when_target_missing(caplog: pytest.LogCaptureFixture) -> None:
    assert _mod.main([*_ARGV, "--class-map", "0:vespa_crabro"]) == 2
    assert "vespa_velutina" in caplog.text


# Exit 2 below comes from the missing dataset, checked after the bee warning.
def test_main_warns_when_bee_missing(caplog: pytest.LogCaptureFixture) -> None:
    _mod.main([*_ARGV, "--class-map", "1:vespa_velutina"])
    assert "apis_mellifera" in caplog.text


def test_main_does_not_warn_when_bee_mapped(caplog: pytest.LogCaptureFixture) -> None:
    _mod.main([*_ARGV, "--class-map", "1:vespa_velutina,2:apis_mellifera"])
    assert "apis_mellifera" not in caplog.text
    assert "Dataset" in caplog.text
