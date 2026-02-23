from dataclasses import dataclass
from datetime import datetime
from typing import List

from core.operator_dashboard.lifecycle_summary import LifecycleOperatorSummary


@dataclass(frozen=True)
class LifecycleAlertPayload:
    """
    Immutable, delivery-agnostic alert payload for lifecycle events.

    This object:
    - Contains no transport logic
    - Encodes severity + message
    - Is safe for Slack / Email / PagerDuty / Audit
    """

    strategy_id: str
    severity: str
    title: str
    message: str
    flags: List[str]
    generated_at: datetime

    @staticmethod
    def from_operator_summary(
        summary: LifecycleOperatorSummary,
        *,
        now: datetime,
    ) -> "LifecycleAlertPayload":
        severity = _infer_severity(summary.flags)

        title = f"Lifecycle Alert — {summary.strategy_id}"

        message = (
            f"Strategy `{summary.strategy_id}` is in state "
            f"`{summary.current_state.value}` for "
            f"{summary.days_in_current_state} days.\n\n"
            f"Flags detected:\n"
            f"{_format_flags(summary.flags)}"
        )

        return LifecycleAlertPayload(
            strategy_id=summary.strategy_id,
            severity=severity,
            title=title,
            message=message,
            flags=list(summary.flags),
            generated_at=now,
        )


# ----------------------------
# Internal helpers
# ----------------------------

def _infer_severity(flags: List[str]) -> str:
    if not flags:
        return "INFO"

    if any("CRITICAL" in f or "RETIRE" in f for f in flags):
        return "CRITICAL"

    if any("CHURN" in f or "STAGNATION" in f for f in flags):
        return "WARNING"

    return "INFO"


def _format_flags(flags: List[str]) -> str:
    if not flags:
        return "- none -"

    return "\n".join(f"- {flag}" for flag in flags)
