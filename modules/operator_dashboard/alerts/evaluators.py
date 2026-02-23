from typing import List

from operator_dashboard.alerts.alert_event import AlertEvent
from operator_dashboard.alerts.alert_types import AlertType
from operator_dashboard.data_contracts import StrategySummaryDTO


def evaluate_alerts(
    *,
    strategies: List[StrategySummaryDTO],
) -> List[AlertEvent]:
    """
    Pure alert evaluation logic.

    Rules:
    ✔ Stateless
    ✔ No dashboard imports
    ✔ No system loaders
    ✔ No side-effects
    """
    alerts: List[AlertEvent] = []

    for s in strategies:
        # Governance pending
        if s.status == "pending_approval":
            alerts.append(
                AlertEvent.now(
                    alert_type=AlertType.GOVERNANCE_PENDING,
                    severity="warning",
                    strategy_id=s.strategy_id,
                    message=f"Strategy {s.strategy_id} awaiting approval",
                )
            )

        # Governance rejected
        if s.approval and s.approval.status == "rejected":
            alerts.append(
                AlertEvent.now(
                    alert_type=AlertType.GOVERNANCE_REJECTED,
                    severity="critical",
                    strategy_id=s.strategy_id,
                    message="Strategy rejected by governance",
                )
            )

        # Kill switch armed
        if s.kill_switch_active:
            alerts.append(
                AlertEvent.now(
                    alert_type=AlertType.KILL_SWITCH_ARMED,
                    severity="critical",
                    strategy_id=s.strategy_id,
                    message="Kill switch is armed",
                )
            )

        # Canary halted
        if s.lifecycle_stage == "canary" and not s.canary_active:
            alerts.append(
                AlertEvent.now(
                    alert_type=AlertType.CANARY_HALTED,
                    severity="critical",
                    strategy_id=s.strategy_id,
                    message="Canary strategy halted",
                )
            )

        # SSR degradation
        if s.paper_ssr is not None and s.paper_ssr < 0.80:
            alerts.append(
                AlertEvent.now(
                    alert_type=AlertType.SSR_DEGRADATION,
                    severity="warning",
                    strategy_id=s.strategy_id,
                    message=f"Paper SSR below threshold: {s.paper_ssr:.2f}",
                    metadata={"paper_ssr": str(s.paper_ssr)},
                )
            )

    return alerts
