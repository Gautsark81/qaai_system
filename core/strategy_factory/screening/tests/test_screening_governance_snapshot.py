from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.screening_governance_snapshot import (
    ScreeningGovernanceBridge,
)


def test_governance_snapshot_contract():
    engine = ScreeningEngine()
    bridge = ScreeningGovernanceBridge()

    result = engine.screen({
        "A": Decimal("3"),
        "B": Decimal("2"),
    })

    snapshot = bridge.build(
        screening_result=result,
        regime="BULL",
    )

    assert snapshot.ranked_strategies == ("A", "B")
    assert snapshot.state_hash == result.state_hash
    assert snapshot.advisory_strength == Decimal("3")
    assert snapshot.regime == "BULL"


def test_governance_snapshot_deterministic():
    engine = ScreeningEngine()
    bridge = ScreeningGovernanceBridge()

    result1 = engine.screen({
        "A": Decimal("3"),
        "B": Decimal("2"),
    })

    result2 = engine.screen({
        "A": Decimal("3"),
        "B": Decimal("2"),
    })

    snap1 = bridge.build(screening_result=result1)
    snap2 = bridge.build(screening_result=result2)

    assert snap1 == snap2