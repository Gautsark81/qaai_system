from core.capital.stress.stress_engine import CapitalStressEngine
from core.capital.stress.shock_models import CapitalShock


def test_capital_stress_reduces_concentration():
    weights = {
        "A": 0.7,
        "B": 0.3,
    }

    shock = CapitalShock(
        name="MARKET_CRASH",
        multiplier=0.5,
    )

    engine = CapitalStressEngine()
    stressed = engine.apply_shock(weights=weights, shock=shock)

    assert abs(sum(stressed.values()) - 1.0) < 1e-6
    assert stressed["A"] > stressed["B"]
