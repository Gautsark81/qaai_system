# core/observability/decision_trace.py

from core.observability.event_bus import EventBus


class DecisionTrace:
    """
    Records why decisions were made.
    """

    @staticmethod
    def record(
        decision: str,
        reason: str,
        context: dict,
        strategy_id: str | None = None,
        symbol: str | None = None,
    ):
        EventBus.emit(
            event_type="DECISION",
            payload={
                "decision": decision,
                "reason": reason,
                "context": context,
            },
            strategy_id=strategy_id,
            symbol=symbol,
        )
