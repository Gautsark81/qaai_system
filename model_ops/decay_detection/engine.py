from typing import List

from .decision import DecayDecision
from .audit import DecayAuditEvent


class LiveDecayDetectionEngine:
    """
    Detects structural decay in live models.
    Produces signals ONLY (no capital / promotion effects).
    """

    def __init__(
        self,
        *,
        detectors: List,
        audit_sink,
        clock,
    ):
        self.detectors = detectors
        self.audit_sink = audit_sink
        self.clock = clock

    def evaluate(self, *, model_id: str, metrics) -> DecayDecision:
        reasons: List[str] = []

        for detector in self.detectors:
            if detector.detect(metrics):
                reasons.append(detector.__class__.__name__)

        if not reasons:
            return DecayDecision(decaying=False, reasons=[])

        self.audit_sink.emit(
            DecayAuditEvent(
                model_id=model_id,
                reasons=reasons,
                timestamp=self.clock.utcnow(),
            )
        )

        return DecayDecision(decaying=True, reasons=reasons)
