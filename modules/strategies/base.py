# modules/strategies/base.py

from datetime import datetime
from typing import Optional

from modules.guardrails.strategy_guard import strategy_import_context
from modules.strategies.intent_validator import validate_intent
from modules.strategies.health.store import StrategyHealthStore
from modules.strategies.health.guard import StrategyKillSwitch
from modules.audit.events import AuditEvent
from modules.audit.sink import AuditSink


# ---------------------------------------------------------------------
# GLOBAL SINGLETONS (PHASE-9 LOCKED, DETERMINISTIC)
# ---------------------------------------------------------------------

_AUDIT_SINK = AuditSink()

_HEALTH_STORE = StrategyHealthStore(
    max_failures=3  # Phase-9 invariant: bounded fault tolerance
)

_KILL_SWITCH = StrategyKillSwitch(_HEALTH_STORE)


# ---------------------------------------------------------------------
# BASE STRATEGY CONTRACT (FINAL)
# ---------------------------------------------------------------------

class BaseStrategy:
    """
    Phase 9 Strategy Contract Anchor.

    GUARANTEES:
    - Deterministic execution
    - Guarded imports (no forbidden layers)
    - Emits ONLY StrategyIntent | None
    - Restart-safe (no internal mutable state)
    - Auto-disabled after repeated failures
    - Side-effects restricted to audit emission
    """

    def __init__(
        self,
        *,
        strategy_id: str,
        version: str,
        symbol: str,
        timeframe: str,
        params: dict,
    ):
        self.strategy_id = strategy_id
        self.version = version
        self.symbol = symbol
        self.timeframe = timeframe
        self.params = params

    # --------------------------------------------------
    # FINAL ENTRYPOINT
    # --------------------------------------------------

    def run(self, *args, **kwargs) -> Optional[object]:
        """
        FINAL execution entrypoint.

        This method MUST NOT be overridden.
        """
        # ---- Hard kill-switch gate (pre-execution)
        if not _KILL_SWITCH.allow_execution(self.strategy_id):
            return None

        try:
            # ---- Guarded execution context
            with strategy_import_context():
                raw_result = self._run(*args, **kwargs)

            # ---- Intent validation (hard contract)
            intent = validate_intent(raw_result)

            # ---- Observational audit only
            if intent is not None:
                _AUDIT_SINK.emit(
                    AuditEvent(
                        timestamp=datetime.utcnow(),
                        category="STRATEGY_INTENT",
                        entity_id=self.strategy_id,
                        message=f"Intent emitted: {intent.side}",
                    )
                )

            return intent

        except Exception as exc:
            # ---- Failure recorded BEFORE propagation
            _HEALTH_STORE.record_failure(self.strategy_id, str(exc))
            raise

    # --------------------------------------------------
    # STRATEGY IMPLEMENTATION HOOK
    # --------------------------------------------------

    def _run(self, *args, **kwargs):
        """
        Strategy implementation hook.

        CONTRACT:
        - Must be pure
        - Must return StrategyIntent | None
        - Must not perform I/O, execution, or mutation
        """
        raise NotImplementedError("Strategy must implement _run()")
