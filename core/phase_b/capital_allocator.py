from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CapitalDecision:
    """
    Advisory-only capital scaling decision.
    """
    dna: str
    confidence: float
    ssr: Optional[float]
    scale: float  # multiplier [0.0 .. 1.0]
    reason: str


class CapitalAllocator:
    """
    Phase B influence engine.
    NEVER grants execution permission.
    """

    def decide(
        self,
        *,
        dna: str,
        confidence: float,
        ssr: Optional[float],
    ) -> CapitalDecision:
        # Conservative default
        scale = 0.5
        reason = "baseline"

        if confidence >= 0.8:
            scale = 1.0
            reason = "high_confidence"
        elif confidence >= 0.6:
            scale = 0.75
            reason = "medium_confidence"
        else:
            scale = 0.25
            reason = "low_confidence"

        # SSR refines, never dominates
        if ssr is not None:
            if ssr < 0.4:
                scale *= 0.5
                reason += "_low_ssr"
            elif ssr > 0.8:
                scale = min(1.0, scale * 1.1)
                reason += "_high_ssr"

        return CapitalDecision(
            dna=dna,
            confidence=confidence,
            ssr=ssr,
            scale=round(scale, 2),
            reason=reason,
        )
