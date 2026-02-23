from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from strategies.base import StrategySignal
from risk.base import RiskDecision
from qaai_system.execution.models import OrderIntent, ExecutionReport
from infra.time_utils import now_ist


@dataclass(slots=True)
class DecisionRecord:
    ts: datetime
    signal: StrategySignal
    risk: RiskDecision
    intent: OrderIntent
    report: ExecutionReport
    extra: Dict[str, Any]


class AuditTrail:
    """
    Supercharged: a compact, structured record of the whole decision chain.

    Hybrid:
      - In live, you can stream these to disk / DB / logging.
      - In backtest, keep them in memory for analysis.
    """

    def __init__(self) -> None:
        self._records: List[DecisionRecord] = []

    def record(
        self,
        signal: StrategySignal,
        risk: RiskDecision,
        intent: OrderIntent,
        report: ExecutionReport,
        extra: Dict[str, Any] | None = None,
    ) -> None:
        self._records.append(
            DecisionRecord(
                ts=now_ist(),
                signal=signal,
                risk=risk,
                intent=intent,
                report=report,
                extra=dict(extra or {}),
            )
        )

    def all(self) -> List[DecisionRecord]:
        return list(self._records)
