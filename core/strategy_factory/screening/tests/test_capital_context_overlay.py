from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.screening_governance_snapshot import (
    ScreeningGovernanceBridge,
)
from core.strategy_factory.screening.capital_context_overlay import (
    CapitalContextOverlay,
)


def test_capital_overlay_contract():
    engine = ScreeningEngine()
    bridge = ScreeningGovernanceBridge()
    overlay = CapitalContextOverlay()

    result = engine.screen({
        "A": Decimal("4"),
        "B": Decimal("2"),
    })

    gov = bridge.build(screening_result=result)

    advisory = overlay.apply(
        governance_snapshot=gov,
        capital_utilization_pct=Decimal("0.5"),
    )

    assert advisory.ranked_strategies == ("A", "B")
    assert advisory.base_state_hash == result.state_hash
    assert advisory.adjusted_advisory_strength == Decimal("2")
    assert advisory.capital_utilization_pct == Decimal("0.5")


def test_capital_overlay_deterministic():
    engine = ScreeningEngine()
    bridge = ScreeningGovernanceBridge()
    overlay = CapitalContextOverlay()

    result = engine.screen({
        "A": Decimal("4"),
    })

    gov = bridge.build(screening_result=result)

    a1 = overlay.apply(
        governance_snapshot=gov,
        capital_utilization_pct=Decimal("0.3"),
    )

    a2 = overlay.apply(
        governance_snapshot=gov,
        capital_utilization_pct=Decimal("0.3"),
    )

    assert a1 == a2


def test_capital_overlay_clamps_bounds():
    engine = ScreeningEngine()
    bridge = ScreeningGovernanceBridge()
    overlay = CapitalContextOverlay()

    result = engine.screen({"A": Decimal("10")})
    gov = bridge.build(screening_result=result)

    a = overlay.apply(
        governance_snapshot=gov,
        capital_utilization_pct=Decimal("2"),
    )

    assert a.adjusted_advisory_strength == Decimal("0")