from datetime import datetime
from typing import Optional

from core.strategy_factory.lifecycle.state_machine import (
    LifecycleState,
    validate_transition,
)
from core.strategy_factory.lifecycle.events import LifecycleEvent

# ➕ ADD (non-intrusive)
from core.evidence.decision_store import DecisionEvidenceStore
from core.strategy_factory.lifecycle.evidence_contracts import (
    LifecycleTransitionEvidence,
)
from core.strategy_factory.lifecycle.evidence_emitter import (
    emit_lifecycle_transition_evidence,
)


class LifecycleEngine:
    """
    OFFLINE autonomous lifecycle engine.
    No execution. No capital. No registry mutation.
    """

    def decide(
        self,
        *,
        strategy_dna: str,
        current_state: LifecycleState,
        fitness: Optional[float] = None,
        fragility: Optional[float] = None,
        evidence_store: Optional[DecisionEvidenceStore] = None,  # ➕ ADD (optional)
    ) -> Optional[LifecycleEvent]:

        # --------------------------------------------------
        # ❄️ Freeze dominates everything
        # --------------------------------------------------
        if fragility is not None and fragility > 0.8:
            if current_state != LifecycleState.FROZEN:
                validate_transition(current_state, LifecycleState.FROZEN)

                event = LifecycleEvent(
                    strategy_dna=strategy_dna,
                    from_state=current_state,
                    to_state=LifecycleState.FROZEN,
                    trigger="fragility",
                    reason="High fragility detected",
                    timestamp=datetime.utcnow(),
                )

                # ➕ Evidence emission (non-blocking, additive)
                if evidence_store is not None:
                    emit_lifecycle_transition_evidence(
                        evidence=LifecycleTransitionEvidence(
                            strategy_id=strategy_dna,
                            from_state=current_state,
                            to_state=LifecycleState.FROZEN,
                            reason=event.reason,
                            transition_id=f"{strategy_dna}:{current_state.value}->FROZEN",
                        ),
                        store=evidence_store,
                    )

                return event

            return None

        # --------------------------------------------------
        # 🚀 Promotion logic (offline)
        # --------------------------------------------------
        if fitness is not None and fitness > 0.7:
            next_state = {
                LifecycleState.CREATED: LifecycleState.SCREENED,
                LifecycleState.SCREENED: LifecycleState.WATCHLISTED,
                LifecycleState.WATCHLISTED: LifecycleState.PAPER,
            }.get(current_state)

            if next_state:
                validate_transition(current_state, next_state)

                event = LifecycleEvent(
                    strategy_dna=strategy_dna,
                    from_state=current_state,
                    to_state=next_state,
                    trigger="fitness",
                    reason="Fitness threshold satisfied",
                    timestamp=datetime.utcnow(),
                )

                # ➕ Evidence emission (non-blocking, additive)
                if evidence_store is not None:
                    emit_lifecycle_transition_evidence(
                        evidence=LifecycleTransitionEvidence(
                            strategy_id=strategy_dna,
                            from_state=current_state,
                            to_state=next_state,
                            reason=event.reason,
                            transition_id=(
                                f"{strategy_dna}:{current_state.value}"
                                f"->{next_state.value}"
                            ),
                        ),
                        store=evidence_store,
                    )

                return event

        return None
