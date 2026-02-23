from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OversightFinding:
    """
    Atomic oversight finding used by detectors
    and correlation engine.
    """

    domain: str                 # capital | governance | lifecycle | regime
    severity: str               # INFO | WARNING | CRITICAL

    summary: str
    detector: str

    evidence_id: Optional[str] = None
