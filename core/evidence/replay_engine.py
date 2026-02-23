# core/evidence/replay_engine.py

from typing import Iterable, List, Any

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.replay_contracts import ReplayFrame
from core.compliance.audit_pack.models import AuditPack


# ---------------------------------------------------------------------
# EXISTING REPLAY LOGIC (UNCHANGED)
# ---------------------------------------------------------------------
def replay_decisions(
    *,
    evidence: Iterable[DecisionEvidence],
) -> List[ReplayFrame]:
    """
    Deterministically reconstruct system decision state over time.

    Rules:
    - Evidence MUST be pre-sorted by timestamp
    - Later evidence overwrites earlier state
    """

    frames: List[ReplayFrame] = []

    capital_state = {}
    governance_state = {}
    market_regime = "UNKNOWN"
    regime_confidence = 0.0

    for e in evidence:
        if e.decision_type == "CAPITAL_ALLOC":
            capital_state[e.strategy_id] = e.approved_weight

        if e.decision_type in ("PAPER", "LIVE", "CANARY"):
            governance_state[e.strategy_id] = e.status

        if e.market_regime:
            market_regime = e.market_regime
            regime_confidence = e.regime_confidence or 0.0

        frames.append(
            ReplayFrame(
                timestamp=e.timestamp,
                capital_allocations=dict(capital_state),
                governance_states=dict(governance_state),
                market_regime=market_regime,
                regime_confidence=regime_confidence,
            )
        )

    return frames


# ---------------------------------------------------------------------
# PHASE 28.2 — COMPLIANCE REPLAY ENGINE (READ-ONLY)
# ---------------------------------------------------------------------
class ReplayEngine:
    """
    Compliance-safe replay engine constructed from an Audit Pack.

    GUARANTEES:
    - READ-ONLY
    - NO execution authority
    - Deterministic
    - Artifact-driven
    """

    def __init__(self, artifacts: list[dict]):
        self._artifacts = list(artifacts)

    # --------------------------------------------------------------
    # Phase 28.2 Adapter
    # --------------------------------------------------------------
    @classmethod
    def from_audit_pack(cls, pack: AuditPack) -> "ReplayEngine":
        """
        Construct a replay engine from a compliance Audit Pack.

        Rules:
        - AuditPack must already be checksummed
        - No execution paths are enabled
        - Artifacts are consumed descriptively
        """
        if not pack.checksum:
            raise ValueError("AuditPack checksum missing or invalid")

        artifacts = [
            {
                "kind": artifact.kind,
                "payload": artifact.payload,
            }
            for artifact in pack.artifacts
        ]

        return cls(artifacts=artifacts)

    # --------------------------------------------------------------
    # Read-only surface
    # --------------------------------------------------------------
    def artifacts(self) -> list[dict]:
        return list(self._artifacts)

    def describe(self) -> dict[str, Any]:
        return {
            "mode": "REPLAY_ONLY",
            "artifact_count": len(self._artifacts),
        }
