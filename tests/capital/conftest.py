import pytest
from uuid import uuid4


class DummySnapshot:
    def __init__(
        self,
        ssr=0.85,
        expectancy=0.4,
        max_drawdown=0.1,
    ):
        self.strategy_id = f"STRAT_{uuid4()}"
        self.strategy_version = "1.0"
        self.ssr = ssr
        self.expectancy = expectancy
        self.max_drawdown = max_drawdown


@pytest.fixture
def snapshot():
    return DummySnapshot()
