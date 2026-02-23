from datetime import datetime
from typing import Optional, Tuple

from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.lifecycle.rules import LifecycleRules
from core.lifecycle.versions import LIFECYCLE_V1


# Canonical forward order — DO NOT CHANGE
_FORWARD_ORDER = [
    LifecycleState.CANDIDATE,
    LifecycleState.PAPER,
    LifecycleState.LIVE,
    LifecycleState.DEGRADED,
    LifecycleState.RETIRED,
]


def _state_index(state: LifecycleState) -> int:
    return _FORWARD_ORDER.index(state)


class LifecycleEngine:
    """
    Phase-B Authoritative Lifecycle Engine

    GUARANTEES:
    - Pure & deterministic (no memory)
    - No backward transitions
    - No skipped states
    - Governance gates LIVE
    - Replay-safe via snapshot evolution (NOT internal state)

    NOTE:
    Exactly-once emission is a Phase-C concern (EventStore).
    """

    def __init__(self, rules: Optional[LifecycleRules] = None):
        self.rules = rules or LifecycleRules()

    def resolve(
        self,
        *,
        snapshot: LifecycleSnapshot,
        now: datetime,
        ssr_status,
        health_status,
        operator_override: Optional[LifecycleState] = None,
        governance_approved: bool = False,
    ) -> Tuple[Optional[LifecycleEvent], LifecycleSnapshot]:

        # --------------------------------------------------
        # TERMINAL STATE
        # --------------------------------------------------
        if snapshot.state == LifecycleState.RETIRED:
            return None, snapshot

        # --------------------------------------------------
        # OPERATOR OVERRIDE (absolute authority)
        # --------------------------------------------------
        if operator_override is not None:
            if operator_override == snapshot.state:
                return None, snapshot

            return (
                LifecycleEvent(
                    strategy_id=snapshot.strategy_id,
                    from_state=snapshot.state,
                    to_state=operator_override,
                    reason="OPERATOR_OVERRIDE",
                    as_of=now,
                ),
                LifecycleSnapshot(
                    strategy_id=snapshot.strategy_id,
                    state=operator_override,
                    since=now,
                    version=LIFECYCLE_V1,
                ),
            )

        # --------------------------------------------------
        # RULE EVALUATION (PURE)
        # --------------------------------------------------
        next_state, reason = self.rules.evaluate(
            current_state=snapshot.state,
            since=snapshot.since,
            now=now,
            ssr_status=ssr_status,
            health_status=health_status,
        )

        # No transition suggested
        if next_state is None:
            return None, snapshot

        # --------------------------------------------------
        # MONOTONICITY GUARANTEE
        # --------------------------------------------------
        if _state_index(next_state) <= _state_index(snapshot.state):
            return None, snapshot

        # --------------------------------------------------
        # GOVERNANCE GATE (LIVE ONLY)
        # --------------------------------------------------
        if next_state == LifecycleState.LIVE and not governance_approved:
            return None, snapshot

        # --------------------------------------------------
        # EMIT EVENT (PURE)
        # --------------------------------------------------
        return (
            LifecycleEvent(
                strategy_id=snapshot.strategy_id,
                from_state=snapshot.state,
                to_state=next_state,
                reason=reason.value if hasattr(reason, "value") else str(reason),
                as_of=now,
            ),
            LifecycleSnapshot(
                strategy_id=snapshot.strategy_id,
                state=next_state,
                since=now,
                version=LIFECYCLE_V1,
            ),
        )
