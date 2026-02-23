from dataclasses import dataclass
from typing import List, Optional

from core.alpha.screening.models.screening_layer import ScreeningLayer
from core.alpha.screening.models.screening_evidence import ScreeningEvidence


@dataclass(frozen=True)
class ScreeningVerdict:
    """
    Immutable verdict for a single symbol.

    This is the ONLY object allowed to flow
    downstream into watchlists.
    """

    symbol: str
    eligible: bool
    failed_layer: Optional[ScreeningLayer]
    confidence: float
    evidence: List[ScreeningEvidence]
    explanation: str

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "eligible": self.eligible,
            "failed_layer": self.failed_layer.value if self.failed_layer else None,
            "confidence": self.confidence,
            "evidence": [e.to_dict() for e in self.evidence],
            "explanation": self.explanation,
        }
