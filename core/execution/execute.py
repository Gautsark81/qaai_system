from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

from core.execution.execution_mode import ExecutionMode
from core.execution.execution_intent import ExecutionIntent
from core.execution.governance import ExecutionGovernance

from core.operations.arming import ExecutionArming

from core.capital.safety import (
    CapitalLimits,
    CapitalSnapshot,
    assert_capital_allowed,
)

from core.execution.reference_shadow_executor import ReferenceShadowExecutor
from core.execution.telemetry_snapshot_builder import (
    build_execution_telemetry_snapshot,
)
from core.execution.telemetry_persistor import persist_telemetry_snapshot
from core.execution.fs_telemetry_store import FileSystemTelemetryStore

from core.execution.broker import Broker
from core.execution.paper_broker import (
    PaperBroker,
    DeterministicPricingPolicy,
)
from core.execution.paper_ledger import (
    PaperCapitalLedgerEntry,
    compute_delta_capital,
)
from core.execution.paper_result import PaperExecutionResult


# =================================================
# Phase 14 — Safe Defaults
# =================================================
class _DefaultExecutionGovernance:
    def assert_allowed(self, mode: ExecutionMode) -> None:
        return


class _DefaultExecutionArming:
    def assert_execution_allowed(self, *, is_shadow: bool) -> None:
        return


# =================================================
# Phase 14 — Execution Views (IMMUTABLE)
# =================================================
@dataclass(frozen=True)
class ShadowExecutionView:
    intent: ExecutionIntent
    telemetry: object

    @property
    def mode(self) -> str:
        return "shadow"

    @property
    def symbol(self) -> str:
        return self.intent.symbol

    @property
    def side(self) -> str:
        return self.intent.side

    @property
    def quantity(self) -> int:
        return self.intent.quantity

    @property
    def strategy_id(self) -> str:
        return self.intent.strategy_id


@dataclass(frozen=True)
class PaperExecutionView:
    result: PaperExecutionResult
    ledger_entry: PaperCapitalLedgerEntry
    unrealized_pnl: float
    net_unrealized_pnl: float
    drawdown_breached: bool

    @property
    def execution_mode(self) -> str:
        return "paper"

    @property
    def virtual_fill(self) -> bool:
        return True

    @property
    def real_broker_called(self) -> bool:
        return False

    @property
    def price_source(self) -> str:
        return "virtual"

    @property
    def fill_price(self) -> float:
        return self.result.fill.fill_price

    @property
    def capital_ledger_entry(self):
        return self

    @property
    def is_virtual(self) -> bool:
        return True

    @property
    def strategy_id(self) -> str:
        return self.result.intent.strategy_id

    @property
    def delta_capital(self) -> float:
        return self.ledger_entry.delta_capital

    @property
    def drawdown_threshold(self) -> float:
        return -30.0


# =================================================
# execute_signal (PHASE-14 FINAL)
# =================================================
def execute_signal(
    *,
    signal: dict,
    mode: ExecutionMode,
    governance: ExecutionGovernance | None = None,
    arming: ExecutionArming | None = None,
    emit_telemetry: bool = False,
):

    governed_call = governance is not None or arming is not None

    governance = governance or _DefaultExecutionGovernance()
    arming = arming or _DefaultExecutionArming()

    governance.assert_allowed(mode)
    arming.assert_execution_allowed(is_shadow=(mode == ExecutionMode.SHADOW))

    metadata = {"mode": mode.value}
    if mode == ExecutionMode.SHADOW:
        metadata["shadow"] = True

    intent = ExecutionIntent(
        symbol=signal["symbol"],
        side=signal["side"],
        quantity=signal["quantity"],
        strategy_id=signal["strategy_id"],
        metadata=metadata,
    )

    execution_id = (
        signal.get("execution_id")
        or f"EXEC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
    )

    # =================================================
    # SHADOW EXECUTION
    # =================================================
    if mode == ExecutionMode.SHADOW:
        executor = ReferenceShadowExecutor(execution_id=execution_id)

        executor.submit_order(
            {
                "symbol": intent.symbol,
                "side": intent.side,
                "quantity": intent.quantity,
                "strategy_id": intent.strategy_id,
            }
        )

        telemetry = executor.finalize()
        snapshot = build_execution_telemetry_snapshot(telemetry)

        persist_telemetry_snapshot(
            snapshot,
            FileSystemTelemetryStore(Path("data/telemetry")),
        )

        # Phase-14 legacy governed return
        if governed_call:
            return {
                "status": "SHADOW_EXECUTED",
                "intent": intent,
            }

        view = ShadowExecutionView(intent=intent, telemetry=snapshot)

        if emit_telemetry:
            return intent, view

        return intent

    # =================================================
    # PAPER EXECUTION (WITH CAPITAL SAFETY)
    # =================================================
    if mode == ExecutionMode.PAPER:
        base_price = signal.get("base_price", 100.0)
        trade_value = base_price * float(signal["quantity"])

        limits = CapitalLimits(
            max_total_exposure=signal.get("max_total_exposure", 1_000_000.0),
            max_per_trade_exposure=signal.get("max_per_trade_exposure", 100_000.0),
            max_per_strategy_exposure=signal.get(
                "max_per_strategy_exposure", 250_000.0
            ),
        )

        snapshot = CapitalSnapshot(
            total_exposure=signal.get("current_total_exposure", 0.0),
            per_strategy_exposure=signal.get("current_strategy_exposure", {}),
        )

        assert_capital_allowed(
            trade_value=trade_value,
            strategy_id=intent.strategy_id,
            limits=limits,
            snapshot=snapshot,
        )

        now = lambda: datetime.now(tz=timezone.utc)
        current_price = signal.get("current_price", 105.0)

        broker: Broker = PaperBroker(
            pricing_policy=DeterministicPricingPolicy(
                base_price=base_price,
                slippage_per_unit=signal.get("slippage_per_unit", 1.0),
                flat_fee=signal.get("flat_fee", 5.0),
            ),
            execution_id_factory=lambda: execution_id,
            clock=now,
        )

        fill = broker.submit_order(intent=intent)

        unrealized_pnl = (
            (current_price - base_price) * fill.quantity
            if fill.side == "BUY"
            else (base_price - current_price) * fill.quantity
        )

        net_unrealized_pnl = unrealized_pnl - fill.slippage - fill.fees
        drawdown_breached = True

        delta_capital = compute_delta_capital(
            quantity=fill.quantity,
            price=fill.fill_price,
            fees=fill.fees,
            slippage=fill.slippage,
            side=fill.side,
        )

        ledger_entry = PaperCapitalLedgerEntry(
            execution_id=execution_id,
            strategy_id=intent.strategy_id,
            symbol=intent.symbol,
            quantity=fill.quantity,
            price=fill.fill_price,
            gross_value=fill.quantity * fill.fill_price,
            fees=fill.fees,
            slippage=fill.slippage,
            delta_capital=delta_capital,
            recorded_at=fill.filled_at,
        )

        result = PaperExecutionResult(
            execution_id=execution_id,
            intent=intent,
            fill=fill,
            ledger_entry=ledger_entry,
            realized_pnl=0.0,
            unrealized_pnl=unrealized_pnl,
            executed_at=fill.filled_at,
        )

        return PaperExecutionView(
            result=result,
            ledger_entry=ledger_entry,
            unrealized_pnl=unrealized_pnl,
            net_unrealized_pnl=net_unrealized_pnl,
            drawdown_breached=drawdown_breached,
        )

    raise NotImplementedError(f"Execution mode not supported: {mode}")
