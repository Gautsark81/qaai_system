# core/strategy_factory/health/resurrection/engine.py

from __future__ import annotations

from typing import Optional

from .policy import ResurrectionPolicy
from .enums import ResurrectionState
from .artifacts import ResurrectionDecisionArtifact


class ResurrectionEngine:
    """
    Resurrection decision engine.

    Responsibilities:
    - Evaluate whether a retired strategy is eligible for resurrection
    - Enforce governance via explicit state transitions
    - Emit immutable decision artifacts for auditability
    - NEVER grant execution access (shadow-only revival)

    This engine mutates StrategyRecord lifecycle state but does not
    control execution permissions.
    """

    def __init__(self, registry):
        """
        Parameters
        ----------
        registry : StrategyRegistry
            Central lifecycle registry (authoritative state store)
        """
        self.registry = registry

    # ======================================================
    # Core Evaluation
    # ======================================================

    def evaluate(self, record, decay_snapshot) -> Optional[object]:
        """
        Evaluate whether a retired strategy should enter resurrection.

        Parameters
        ----------
        record : StrategyRecord
            Strategy currently in RETIRED state
        decay_snapshot : DecaySnapshot
            Latest decay diagnostics

        Returns
        -------
        StrategyRecord | None
            Updated strategy record if eligible, else None
        """

        # -------------------------------
        # Policy Gate
        # -------------------------------
        if not ResurrectionPolicy.is_eligible(record, decay_snapshot):
            return None

        # -------------------------------
        # Decision Reasoning
        # -------------------------------
        reason = ResurrectionPolicy.reason(decay_snapshot)

        artifact = ResurrectionDecisionArtifact.from_inputs(
            record=record,
            decay_snapshot=decay_snapshot,
            reason=reason,
        )

        # -------------------------------
        # Registry State Transition
        # -------------------------------
        self.registry.mark_resurrection_candidate(
            record.dna,
            state=ResurrectionState.RESURRECTION_CANDIDATE,
            reason=reason,
            artifact=artifact,
        )

        # Re-fetch ensures authoritative state view
        updated_record = self.registry.get(record.dna)

        return updated_record

    # ======================================================
    # Shadow Promotion
    # ======================================================

    def promote_to_shadow(self, record) -> None:
        """
        Promote a resurrection candidate into shadow revival.

        Shadow revival rules:
        - No capital
        - No execution access
        - Metrics only
        """

        self.registry.transition_state(
            record.dna,
            ResurrectionState.REVIVAL_SHADOW,
        )
