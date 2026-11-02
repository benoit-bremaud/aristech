"""Notification port."""

from typing import Protocol

from aristech.application.attack_episode import AttackEpisode
from aristech.domain import Detection


class Notifier(Protocol):
    """Reports decisions to the outside world (log, message, dashboard)."""

    def notify_detection(self, detection: Detection) -> None:
        """A target at or above the operating threshold: the system would act."""
        ...

    def notify_abstention(self, detection: Detection) -> None:
        """A target seen below the operating threshold: not acted on (ADR-0009)."""
        ...

    def notify_attack_started(self, episode: AttackEpisode) -> None:
        """An attack episode opened: the single alert of that episode (ADR-0031)."""
        ...

    def notify_attack_ended(self, episode: AttackEpisode) -> None:
        """The episode closed: its summary (duration, peak, total), never a new alert."""
        ...
