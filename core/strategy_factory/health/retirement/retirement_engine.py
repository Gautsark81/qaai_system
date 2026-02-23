from datetime import datetime
from typing import Dict, List

from core.strategy_factory.health.retirement.retirement_state import (
    RetirementState,
    ALLOWED_TRANSITIONS,
)
from core.strategy_factory.health.retirement.retirement_record import RetirementRecord
from core.strategy_factory.health.retirement.cooldown_tracker import CooldownTracker


class StrategyRetirementEngine:
    def __init__(self):
        self._states: Dict[str, RetirementState] = {}
        self._cooldowns: Dict[str, CooldownTracker] = {}
        self._history: Dict[str, List[RetirementRecord]] = {}

    def current_state(self, strategy_id: str) -> RetirementState:
        return self._states.get(strategy_id, RetirementState.ACTIVE)

    def transition(
        self,
        strategy_id: str,
        to_state: RetirementState,
        reason: str,
        trigger: str,
        metrics: dict,
        actor: str = "system",
    ) -> RetirementRecord:

        from_state = self.current_state(strategy_id)

        if to_state not in ALLOWED_TRANSITIONS.get(from_state, set()):
            raise ValueError(f"Illegal transition: {from_state} → {to_state}")

        record = RetirementRecord(
            strategy_id=strategy_id,
            from_state=from_state,
            to_state=to_state,
            reason_code=reason,
            trigger_source=trigger,
            metrics_snapshot=metrics,
            actor=actor,
            timestamp=datetime.utcnow(),
        )

        self._states[strategy_id] = to_state
        self._history.setdefault(strategy_id, []).append(record)

        if to_state == RetirementState.COOLING:
            self._cooldowns[strategy_id] = CooldownTracker(
                started_at=datetime.utcnow(), duration_days=7
            )

        return record

    def is_tradeable(self, strategy_id: str) -> bool:
        return self.current_state(strategy_id) == RetirementState.ACTIVE

    def retirement_history(self, strategy_id: str) -> List[RetirementRecord]:
        return self._history.get(strategy_id, [])
