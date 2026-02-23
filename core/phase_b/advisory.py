from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AdvisorySignal:
    """
    Advisory output from Phase B.
    NEVER executable.
    """
    dna: str
    confidence: float
    note: Optional[str] = None
