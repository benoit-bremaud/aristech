"""Legal-floor decision rule applied to every detection."""

from enum import Enum

from aristech.domain import Detection


class Decision(str, Enum):
    """What the system should do about a single detection."""

    ACT = "act"
    ABSTAIN = "abstain"
    IGNORE = "ignore"


def decide(detection: Detection, confidence_threshold: float) -> Decision:
    """Map a detection to an action under the legal-floor abstention policy.

    A target (`VESPA_VELUTINA`) at or above the confidence threshold is the only
    case that triggers action. An uncertain target (below threshold) **abstains**
    rather than acting — "better a missed shot than an illegal one", since acting
    on a misread bee is a criminal risk. Any non-target species is ignored.
    """
    if not detection.is_threat():
        return Decision.IGNORE
    if detection.confidence >= confidence_threshold:
        return Decision.ACT
    return Decision.ABSTAIN
