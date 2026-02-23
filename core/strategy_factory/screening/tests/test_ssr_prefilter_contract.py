from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.ssr_prefilter import SSRPreFilter


def test_ssr_prefilter_contract():
    engine = ScreeningEngine()
    prefilter = SSRPreFilter()

    base = engine.screen({
        "A": Decimal("3.0"),
        "B": Decimal("2.0"),
        "C": Decimal("1.0"),
    })

    ssr_map = {
        "A": Decimal("0.9"),
        "B": Decimal("0.5"),
        "C": Decimal("0.2"),
    }

    result = prefilter.filter(
        base,
        ssr_map=ssr_map,
        threshold=Decimal("0.5"),
    )

    assert all(s.strategy_dna in {"A", "B"} for s in result.scores)
    assert result.state_hash is not None