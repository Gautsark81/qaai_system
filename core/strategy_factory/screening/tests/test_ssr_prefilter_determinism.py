from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.ssr_prefilter import SSRPreFilter


def test_ssr_prefilter_deterministic():
    engine = ScreeningEngine()
    prefilter = SSRPreFilter()

    base = engine.screen({
        "A": Decimal("3.0"),
        "B": Decimal("2.0"),
    })

    ssr_map = {
        "A": Decimal("0.9"),
        "B": Decimal("0.4"),
    }

    r1 = prefilter.filter(base, ssr_map, Decimal("0.5"))
    r2 = prefilter.filter(base, ssr_map, Decimal("0.5"))

    assert r1.state_hash == r2.state_hash