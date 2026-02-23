import pytest
from datetime import datetime

from core.strategy_factory.capital.throttling import (
    evaluate_capital_throttle,
)


def test_throttle_requires_governance_chain():

    with pytest.raises(ValueError):
        evaluate_capital_throttle(
            governance_chain_id="",
            strategy_dna="DNA1",
            requested_capital=100000,
            last_allocation_at=None,
            cooldown_seconds=60,
            now=datetime.utcnow(),
        )