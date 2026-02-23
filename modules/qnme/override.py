# modules/qnme/override.py
from typing import Dict, Any

class MetaCognitiveOverride:
    """
    Layer 11: final safety brain.
    Deterministic rules plus hook for learned policy.
    """

    def __init__(self, risk_engine=None):
        self.risk_engine = risk_engine

    def evaluate(self, regime: Dict[str, Any], anomaly_flag: bool, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an action: {"action":"allow"|"soft_halt"|"halt", "reason": "..."}
        """
        if self.risk_engine and self.risk_engine.should_halt():
            return {"action": "halt", "reason": "risk_engine_cvar_exceeded"}
        if anomaly_flag:
            return {"action": "soft_halt", "reason": "anomaly_detected"}
        # default allow
        return {"action": "allow", "reason": "ok"}
