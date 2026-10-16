from dataclasses import dataclass

from aristech.application.decision import Decision, decide
from aristech.application.ports import HornetDetector, Notifier, VideoSource


@dataclass(frozen=True, slots=True)
class DetectHornetVisualConfig:
    confidence_threshold: float = 0.5

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class DetectionRun:
    """Outcome of a run: how many targets were acted on and abstained on
    (ADR-0009). Counts, not lists: a camera stream never ends, so keeping
    every detection would grow memory without bound."""

    threats: int = 0
    abstentions: int = 0


class DetectHornetVisual:
    """Use case : consomme les frames d'une source vidéo, applique un
    détecteur ML, et notifie chaque menace (ACT) et chaque abstention (cible sous le
    seuil, ABSTAIN) ; les autres espèces sont ignorées.

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

    def run(self) -> DetectionRun:
        threats = abstentions = 0
        try:
            threshold = self._config.confidence_threshold
            for frame in self._video.frames():
                for detection in self._detector.detect(frame):
                    decision = decide(detection, threshold)
                    if decision is Decision.ACT:
                        self._notifier.notify_detection(detection)
                        threats += 1
                    elif decision is Decision.ABSTAIN:
                        self._notifier.notify_abstention(detection)
                        abstentions += 1
        finally:
            self._video.close()
        return DetectionRun(threats=threats, abstentions=abstentions)
