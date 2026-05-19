from dataclasses import dataclass

from aristech.application.ports import HornetDetector, Notifier, VideoSource
from aristech.domain import Detection


@dataclass(frozen=True, slots=True)
class DetectHornetVisualConfig:
    confidence_threshold: float = 0.5

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be in [0, 1]")


class DetectHornetVisual:
    """Use case : consomme les frames d'une source vidéo, applique un
    détecteur ML, et notifie pour chaque détection au-dessus du seuil.

    Toutes les dépendances sont injectées (DIP) et abstraites par des
    Protocols (ISP) : on peut substituer caméra, modèle et canal de
    notification sans toucher au code de ce use case (OCP).
    """

    def __init__(
        self,
        video: VideoSource,
        detector: HornetDetector,
        notifier: Notifier,
        config: DetectHornetVisualConfig | None = None,
    ) -> None:
        self._video = video
        self._detector = detector
        self._notifier = notifier
        self._config = config or DetectHornetVisualConfig()

    def run(self) -> list[Detection]:
        accepted: list[Detection] = []
        try:
            for frame in self._video.frames():
                for detection in self._detector.detect(frame):
                    if (
                        detection.is_threat()
                        and detection.confidence >= self._config.confidence_threshold
                    ):
                        self._notifier.notify_detection(detection)
                        accepted.append(detection)
        finally:
            self._video.close()
        return accepted
