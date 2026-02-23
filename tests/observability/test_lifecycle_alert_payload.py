from datetime import datetime

from core.lifecycle.contracts.enums import LifecycleState
from core.operator_dashboard.lifecycle_summary import LifecycleOperatorSummary
from core.observability.notifications.lifecycle_alert_payload import (
    LifecycleAlertPayload,
)


def test_alert_payload_from_operator_summary():
    now = datetime.utcnow()

    summary = LifecycleOperatorSummary(
        strategy_id="s1",
        current_state=LifecycleState.PAPER,
        days_in_current_state=7,
        flags=["STAGNATION_WARNING"],
    )

    payload = LifecycleAlertPayload.from_operator_summary(
        summary=summary,
        now=now,
    )

    assert payload.strategy_id == "s1"
    assert payload.severity == "WARNING"
    assert "Lifecycle Alert" in payload.title
    assert "STAGNATION_WARNING" in payload.message
    assert payload.flags == ["STAGNATION_WARNING"]
    assert payload.generated_at == now
