from __future__ import annotations

from dataclasses import dataclass

from core.execution.execution_intent import ExecutionIntent
from core.execution.paper_capital_ledger import PaperCapitalLedgerEntry


@dataclass(frozen=True)
class PaperExecutionResult:
    """
    Result of a paper (virtual) execution.

    Properties:
    - No real broker interaction
    - Virtual fill only
    - Virtual capital mutation
    - Deterministic pricing
    - Deterministic PnL and costs
    - Deterministic drawdown flagging
    """

    execution_mode: str
    intent: ExecutionIntent
    virtual_fill: bool
    real_broker_called: bool
    capital_ledger_entry: PaperCapitalLedgerEntry

    # Phase 2
    fill_price: float
    price_source: str

    # Phase 3
    current_price: float
    unrealized_pnl: float

    # Phase 4
    slippage_cost: float
    fee_cost: float
    net_unrealized_pnl: float

    # Phase 5
    drawdown_threshold: float
    drawdown_breached: bool
