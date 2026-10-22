import argparse

import pytest

from aristech.domain import RigState
from aristech.interface.cli import record

_ARGS = [
    "--rig-id", "rig-1", "--hive-id", "hive-a", "--site", "home",
    "--latitude", "48.85", "--longitude", "2.35", "--output", "/tmp/seg",
]  # fmt: skip


class _FakeCampaign:
    def __init__(self, interrupt_after: int | None = None) -> None:
        self.ticks = 0
        self.closed = False
        self._interrupt_after = interrupt_after

    def tick(self) -> RigState:
        if self._interrupt_after is not None and self.ticks >= self._interrupt_after:
            raise KeyboardInterrupt
        self.ticks += 1
        return RigState.RECORDING

    def close(self) -> None:
        self.closed = True


def test_run_ticks_then_closes() -> None:
    campaign = _FakeCampaign()

    record.run(campaign, sleep=lambda _: None, max_ticks=3)  # type: ignore[arg-type]

    assert campaign.ticks == 3
    assert campaign.closed


def test_interrupt_still_closes() -> None:
    campaign = _FakeCampaign(interrupt_after=2)

    record.run(campaign, sleep=lambda _: None)  # type: ignore[arg-type]

    assert campaign.ticks == 2
    assert campaign.closed


def test_main_parses_arguments_and_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[argparse.Namespace] = []
    campaign = _FakeCampaign(interrupt_after=1)

    def build(args: argparse.Namespace) -> _FakeCampaign:
        seen.append(args)
        return campaign

    assert record.main(_ARGS, build=build) == 0  # type: ignore[arg-type]
    assert seen[0].hive_id == "hive-a"
    assert seen[0].longitude == 2.35
    assert campaign.closed


def test_build_campaign_wires_real_adapters(tmp_path: object) -> None:
    args = argparse.Namespace(
        rig_id="rig-1",
        hive_id="hive-a",
        site="home",
        latitude=48.85,
        longitude=2.35,
        software_version="abc",
        audio_device=None,
        output=str(tmp_path),
    )

    campaign = record.build_campaign(args)

    assert campaign.state is RigState.IDLE
