"""`aristech-record`: composition root of the capture rig (UC7, spec capture-rig)."""

import argparse
import logging
import time
from collections.abc import Callable
from pathlib import Path

from aristech.application.use_cases import CampaignConfig, RecordCampaign

_TICK_SECONDS = 1.0


def build_campaign(args: argparse.Namespace) -> RecordCampaign:
    """Wire the real adapters; imports the `capture` infrastructure lazily."""
    from aristech.infrastructure.capture import (
        FileSegmentStore,
        Picamera2Recorder,
        SoundDeviceRecorder,
        SystemClock,
    )

    config = CampaignConfig(
        rig_id=args.rig_id,
        hive_id=args.hive_id,
        site=args.site,
        latitude=args.latitude,
        longitude=args.longitude,
        software_version=args.software_version,
    )
    return RecordCampaign(
        config,
        SystemClock(),
        Picamera2Recorder(),
        SoundDeviceRecorder(device=args.audio_device),
        FileSegmentStore(Path(args.output)),
    )


def run(
    campaign: RecordCampaign,
    sleep: Callable[[float], None] = time.sleep,
    max_ticks: int | None = None,
) -> None:
    """Tick until interrupted (or `max_ticks`, for tests); always closes the campaign."""
    ticks = 0
    try:
        while max_ticks is None or ticks < max_ticks:
            campaign.tick()
            ticks += 1
            sleep(_TICK_SECONDS)
    except KeyboardInterrupt:
        logging.getLogger("aristech.capture").info("stopped by the operator")
    finally:
        campaign.close()


def main(
    argv: list[str] | None = None,
    build: Callable[[argparse.Namespace], RecordCampaign] = build_campaign,
) -> int:
    """Parse the arguments and record until interrupted; returns the exit code."""
    parser = argparse.ArgumentParser(prog="aristech-record")
    parser.add_argument("--rig-id", required=True)
    parser.add_argument("--hive-id", required=True)
    parser.add_argument("--site", required=True)
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True, help="degrees, positive east")
    parser.add_argument("--output", required=True, help="segment root (the SSD mount)")
    parser.add_argument("--audio-device", default=None, help="ALSA device; default input if unset")
    parser.add_argument("--software-version", default="unknown", help="git SHA, for sidecars")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    run(build(args))
    return 0
