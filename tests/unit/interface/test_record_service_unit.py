"""The systemd unit of the capture rig restarts the recorder and passes valid arguments."""

import configparser
import re
from pathlib import Path

import pytest

from aristech.interface.cli import record

_DEPLOY = Path(__file__).resolve().parents[3] / "deploy" / "systemd"


def _unit() -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str  # type: ignore[assignment,method-assign]
    parser.read(_DEPLOY / "aristech-record.service")
    return parser


def _env_example() -> dict[str, str]:
    lines = (_DEPLOY / "record.env.example").read_text().splitlines()
    pairs = [line.split("=", 1) for line in lines if line and not line.startswith("#")]
    return {key: value for key, value in pairs}


def test_unit_restarts_always_and_starts_at_boot() -> None:
    unit = _unit()
    assert unit["Service"]["Restart"] == "always"
    assert unit["Unit"]["StartLimitIntervalSec"] == "0"
    assert unit["Install"]["WantedBy"] == "multi-user.target"


def test_unit_stops_with_sigint_so_the_open_segment_is_closed() -> None:
    assert _unit()["Service"]["KillSignal"] == "SIGINT"


def test_exec_start_arguments_parse_with_the_example_env(monkeypatch: pytest.MonkeyPatch) -> None:
    env = _env_example()
    exec_start = _unit()["Service"]["ExecStart"]
    used = set(re.findall(r"\$\{(\w+)\}", exec_start))
    assert used == set(env)
    argv = re.sub(r"\$\{(\w+)\}", lambda m: env[m.group(1)], exec_start).split()[1:]
    seen: dict[str, object] = {}
    monkeypatch.setattr(record, "run", lambda campaign: None)
    assert record.main(argv, build=lambda args: seen.setdefault("args", args)) == 0  # type: ignore[arg-type,return-value]
    assert vars(seen["args"])["rig_id"] == env["ARISTECH_RIG_ID"]
