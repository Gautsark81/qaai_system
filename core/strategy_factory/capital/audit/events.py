from datetime import datetime, timezone

from .models import ThrottleDecisionEvent


def build_throttle_event(
    strategy_id: str,
    requested: float,
    approved: float,
    throttle_type: str,
    reason: str,
    stability_score: float,
) -> ThrottleDecisionEvent:

    return ThrottleDecisionEvent(
        strategy_id=strategy_id,
        requested_capital=requested,
        approved_capital=approved,
        throttle_type=throttle_type,
        throttle_reason=reason,
        stability_score=stability_score,
        created_at=datetime.now(timezone.utc).isoformat(),
    )