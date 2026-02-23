from datetime import datetime

from core.v2.paper_trading.execution.execution_engine import ExecutionEngine
from core.v2.paper_trading.execution.paper_broker import PaperBroker
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState
from core.v2.paper_trading.orders.order_book import OrderBook
from core.v2.paper_trading.orchestration.paper_orchestrator import PaperOrchestrator
from core.v2.paper_trading.pnl.ledger import PnLLedger


def test_orchestrator_runs_promoted_cycle():
    def price_provider(symbol, ts):
        return 100.0

    broker = PaperBroker(price_provider=price_provider)
    engine = ExecutionEngine(
        broker=broker,
        order_book=OrderBook(),
    )
    ledger = PnLLedger()
    lifecycle = StrategyLifecycle(strategy_id="s1")

    orchestrator = PaperOrchestrator(
        execution_engine=engine,
        pnl_ledger=ledger,
        lifecycle=lifecycle,
    )

    cycle = orchestrator.run_cycle(
        strategy_id="s1",
        promoted=True,
        symbol="AAPL",
        side="BUY",
    )

    assert cycle.orders_created == 1
    assert cycle.fills_created == 1
    assert len(ledger.entries()) == 1
    assert lifecycle.state == LifecycleState.PAPER_ACTIVE


def test_orchestrator_skips_unpromoted():
    broker = PaperBroker(price_provider=lambda s, t: 100.0)
    engine = ExecutionEngine(
        broker=broker,
        order_book=OrderBook(),
    )
    ledger = PnLLedger()
    lifecycle = StrategyLifecycle(strategy_id="s2")

    orchestrator = PaperOrchestrator(
        execution_engine=engine,
        pnl_ledger=ledger,
        lifecycle=lifecycle,
    )

    cycle = orchestrator.run_cycle(
        strategy_id="s2",
        promoted=False,
        symbol="AAPL",
        side="BUY",
    )

    assert cycle.orders_created == 0
    assert cycle.fills_created == 0
    assert ledger.entries() == []
