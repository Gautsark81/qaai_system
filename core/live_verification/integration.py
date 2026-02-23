from __future__ import annotations

import threading
from typing import Any, List

from .execution_trace_collector import ExecutionTraceCollector
from .live_proof_artifact import LiveProofBuilder
from .proof_registry import LiveProofRegistry
from .models import LiveProofArtifact


class LiveVerificationEngine:
    """
    Non-intrusive integration layer.
    Does not control execution.
    Only observes and records.

    Thread-safe global singleton.
    """

    _instance: "LiveVerificationEngine | None" = None
    _lock = threading.Lock()

    # ------------------------------------------------------------------
    # Singleton Access
    # ------------------------------------------------------------------

    @classmethod
    def global_instance(cls) -> "LiveVerificationEngine":
        """
        Returns the shared singleton instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self):
        # Prevent accidental direct instantiation of multiple instances
        if LiveVerificationEngine._instance is not None:
            raise RuntimeError(
                "Use LiveVerificationEngine.global_instance()"
            )

        self._collector = ExecutionTraceCollector()
        self._builder = LiveProofBuilder()
        self._registry = LiveProofRegistry()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        *,
        strategy_dna: str,
        capital_decision: Any,
        risk_verdict: Any,
        execution_intent: Any,
        router_call_payload: Any,
        mode: str,
    ) -> LiveProofArtifact:

        trace = self._collector.collect(
            strategy_dna=strategy_dna,
            capital_decision=capital_decision,
            risk_verdict=risk_verdict,
            execution_intent=execution_intent,
            router_call_payload=router_call_payload,
            mode=mode,
        )

        artifact = self._builder.build(trace)
        self._registry.append(artifact)

        return artifact

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def list_artifacts(self) -> List[LiveProofArtifact]:
        return self._registry.list()

    # ------------------------------------------------------------------
    # Test Support (Controlled Environment Only)
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Clears registry state.

        ONLY for controlled test environments.
        Never use in production.
        """
        self._registry._artifacts.clear()