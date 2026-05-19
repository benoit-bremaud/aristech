from typing import Protocol

from aristech.domain import AudioSample, Species


class SoundClassifier(Protocol):
    def classify(self, sample: AudioSample) -> tuple[Species, float]: ...
