from __future__ import annotations

from typing import Iterable, Optional

from .contracts import (
    KillAction,
    KillDecision,
    KillScope,
    KillSeverity,
    KillSignal,
)


# 🔒 AUTHORITATIVE PRIORITY ORDER (HIGH → LOW)
_PRIORITY = [
    KillSeverity.CRITICAL,
    KillSeverity.HIGH,
    KillSeverity.MEDIUM,
    KillSeverity.LOW,
]


def evaluate_kill_matrix(
    signals: Iterable[KillSignal],
) -> KillDecision:
    """
    Pure, deterministic kill-switch matrix.
    Highest-severity signal ALWAYS wins.
    """

    signals = list(signals)
    if not signals:
        return KillDecision(
            allowed=True,
            action=KillAction.CONTINUE,
            scope=KillScope.SYSTEM,
            reason="No kill conditions triggered",
        )

    # Sort by severity priority
    def severity_rank(sig: KillSignal) -> int:
        return _PRIORITY.index(sig.severity)

    signals.sort(key=severity_rank)

    winner: KillSignal = signals[0]

    if winner.action == KillAction.HALT:
        return KillDecision(
            allowed=False,
            action=KillAction.HALT,
            scope=winner.scope,
            reason=winner.reason,
            triggered_by=winner.source,
        )

    if winner.action == KillAction.THROTTLE:
        return KillDecision(
            allowed=True,
            action=KillAction.THROTTLE,
            scope=winner.scope,
            reason=winner.reason,
            triggered_by=winner.source,
        )

    return KillDecision(
        allowed=True,
        action=KillAction.CONTINUE,
        scope=KillScope.SYSTEM,
        reason="Kill matrix evaluated clean",
    )
