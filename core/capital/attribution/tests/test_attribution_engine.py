from core.capital.attribution.attribution_engine import CapitalAttributionEngine
from core.capital.allocation.allocator import StrategyCapitalSignal


def test_capital_attribution_is_deterministic():
    signals = {
        "A": StrategyCapitalSignal(1.0, 1.0, 1.0),
        "B": StrategyCapitalSignal(0.5, 0.5, 0.5),
    }

    weights = {"A": 0.8, "B": 0.2}

    engine = CapitalAttributionEngine()
    records = engine.explain(signals=signals, weights=weights)

    assert records["A"].final_weight == 0.8
    assert records["A"].raw_score == 1.0

    assert records["B"].final_weight == 0.2
    assert records["B"].raw_score == 0.125
