import pytest

from core.paper_trading.engine import PaperTradingEngine
from core.paper_trading.broker import PaperBroker
from core.paper_trading.ledger import PaperLedger
from core.execution.execution_guard import ExecutionGuard

from core.capital.allocator_v3.allocator import CapitalAllocatorV3
from core.capital.allocator_v3.contracts import StrategyCapitalProfile
from core.strategy_factory.fitness import FitnessResult
from core.regime.taxonomy import MarketRegime


def test_order_blocked_when_no_capital_allocation():
    engine = PaperTradingEngine(
        broker=PaperBroker(),
        ledger=PaperLedger(),
        execution_guard=ExecutionGuard(),
        capital_allocator=CapitalAllocatorV3(),
    )

    profiles = [
        StrategyCapitalProfile("dna-1", max_allocation=0.5, min_fitness=0.1),
    ]

    fitness = {
        "dna-1": FitnessResult(0.9, 0.0, False),
    }

    decision = engine.allocate_capital(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    with pytest.raises(RuntimeError):
        engine.submit_order(
            dna="dna-1",
            symbol="AAPL",
            qty=10,
            side="BUY",
            price=100.0,
            capital_decision=decision,
        )


def test_order_executes_when_capital_present():
    engine = PaperTradingEngine(
        broker=PaperBroker(),
        ledger=PaperLedger(),
        execution_guard=ExecutionGuard(),
        capital_allocator=CapitalAllocatorV3(),
    )

    profiles = [
        StrategyCapitalProfile("dna-2", max_allocation=0.5, min_fitness=0.1),
    ]

    fitness = {
        "dna-2": FitnessResult(0.9, 0.0, True),
    }

    decision = engine.allocate_capital(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    result = engine.submit_order(
        dna="dna-2",
        symbol="AAPL",
        qty=10,
        side="BUY",
        price=100.0,
        capital_decision=decision,
    )

    assert result["status"] == "FILLED"
