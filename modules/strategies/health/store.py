# modules/strategies/health/store.py

from datetime import datetime
from typing import Dict

from modules.strategies.health.types import StrategyHealth, StrategyState
from modules.strategies.health.persistent_store import PersistentHealthAdapter
from modules.audit.events import AuditEvent
from modules.audit.sink import AuditSink


_AUDIT = AuditSink()


class StrategyHealthStore:
    """
    Deterministic strategy health store with optional persistence.

    Semantics:
    - In-memory behavior identical to Phase G
    - Persistence is best-effort
    """

    def __init__(self, *, max_failures: int, persist_path: str | None = None):
        self._max_failures = max_failures
        self._adapter = (
            PersistentHealthAdapter(persist_path) if persist_path else None
        )

        self._data: Dict[str, StrategyHealth] = (
            self._adapter.load() if self._adapter else {}
        )

    def _persist(self) -> None:
        if self._adapter:
            self._adapter.save(self._data)

    def get(self, strategy_id: str) -> StrategyHealth:
        return self._data.get(
            strategy_id,
            StrategyHealth(
                state=StrategyState.ACTIVE,
                failure_count=0,
                last_reason=None,
            ),
        )

    def record_failure(self, strategy_id: str, reason: str) -> StrategyHealth:
        prev = self.get(strategy_id)
        failures = prev.failure_count + 1

        if failures >= self._max_failures:
            state = StrategyState.DISABLED

            _AUDIT.emit(
                AuditEvent(
                    timestamp=datetime.utcnow(),
                    category="STRATEGY_DISABLED",
                    entity_id=strategy_id,
                    message=reason,
                )
            )
        else:
            state = prev.state

        health = StrategyHealth(
            state=state,
            failure_count=failures,
            last_reason=reason,
        )

        self._data[strategy_id] = health
        self._persist()
        return health

    def quarantine(self, strategy_id: str, reason: str) -> StrategyHealth:
        health = StrategyHealth(
            state=StrategyState.QUARANTINED,
            failure_count=self.get(strategy_id).failure_count,
            last_reason=reason,
        )
        self._data[strategy_id] = health
        self._persist()
        return health
