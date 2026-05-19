from typing import Protocol

from aristech.domain import Detection


class Notifier(Protocol):
    def notify_detection(self, detection: Detection) -> None: ...
