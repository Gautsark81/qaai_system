import pytest
from uuid import uuid4
from datetime import datetime


class DummySnapshot:
    def __init__(
        self,
        *,
        ssr=0.85,
        total_trades=50,
        expectancy=0.3,
        profit_factor=1.8,
        max_drawdown=0.1,
        risk_blocks=0,
    ):
        self.strategy_id = "STRAT_X"
        self.strategy_version = "1.0.0"
        self.snapshot_id = uuid4()

        self.ssr = ssr
        self.total_trades = total_trades
        self.expectancy = expectancy
        self.profit_factor = profit_factor
        self.max_drawdown = max_drawdown
        self.risk_blocks = risk_blocks

        self.created_at = datetime.utcnow()


@pytest.fixture
def dummy_snapshot():
    return DummySnapshot()


@pytest.fixture
def dummy_snapshots():
    return [
        DummySnapshot(ssr=0.82),
        DummySnapshot(ssr=0.88),
        DummySnapshot(ssr=0.91),
    ]
