# core/execution/replay/engine.py

from abc import ABC, abstractmethod
from typing import List

from core.execution.replay.envelope import ReplayEnvelope
from core.execution.replay.results import ReplayResult

from core.compliance.audit_pack.models import AuditPack
from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.replay_engine import replay_decisions


class ReplayEngine(ABC):
    """
    Deterministic replay engine interface.

    NOTE:
    Phase 28.2 extends this interface with a COMPLIANCE-ONLY
    construction path that MUST remain read-only.
    """

    # ------------------------------------------------------------------
    # CORE EXECUTION REPLAY INTERFACE
    # ------------------------------------------------------------------
    @abstractmethod
    def run(self, envelope: ReplayEnvelope) -> ReplayResult:
        """
        Run a deterministic replay.

        Must:
        - never perform IO
        - never mutate execution state
        - never raise into callers
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # PHASE 28.2 — COMPLIANCE ENTRY POINT
    # ------------------------------------------------------------------
    @classmethod
    def from_audit_pack(cls, pack: AuditPack) -> "ReplayEngine":
        """
        Construct a READ-ONLY replay engine from a compliance AuditPack.

        Guarantees:
        - Deterministic
        - No execution authority
        - No mutation
        """

        if not pack.checksum:
            raise ValueError("AuditPack checksum missing or invalid")

        decision_evidence: List[DecisionEvidence] = []

        for artifact in pack.artifacts:
            if artifact.kind == "DECISION_EVIDENCE":
                decision_evidence.extend(artifact.payload)

        return _ComplianceReplayEngine(decision_evidence)


# ======================================================================
# INTERNAL — COMPLIANCE REPLAY IMPLEMENTATION
# ======================================================================

class _ComplianceReplayEngine(ReplayEngine):
    """
    Internal replay engine used ONLY for compliance / audit replay.

    This class:
    - MUST remain private
    - MUST never execute trades
    - MUST never accept ReplayEnvelope
    """

    def __init__(self, evidence: List[DecisionEvidence]):
        self._evidence = list(evidence)

    def run(self, envelope: ReplayEnvelope) -> ReplayResult:
        """
        Compliance replay does not accept execution envelopes.
        """
        raise RuntimeError("Compliance replay engine does not support execution envelopes")

    def replay(self):
        """
        Deterministically replay decisions for audit purposes.
        """
        return replay_decisions(evidence=self._evidence)
