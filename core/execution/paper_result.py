# core/execution/paper_result.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.execution.execution_intent import ExecutionIntent
from core.execution.broker import BrokerFill
from core.execution.paper_ledger import PaperCapitalLedgerEntry


# -------------------------------------------------
# Paper Execution Result (Immutable)
# -------------------------------------------------

@dataclass(frozen=True)
class PaperExecutionResult:
    """
    Immutable result of a paper execution.

    This is the canonical object passed to:
    - telemetry
    - replay
    - dashboard
    """

    execution_id: str
    intent: ExecutionIntent
    fill: BrokerFill
    ledger_entry: PaperCapitalLedgerEntry

    realized_pnl: float
    unrealized_pnl: float

    executed_at: datetime
