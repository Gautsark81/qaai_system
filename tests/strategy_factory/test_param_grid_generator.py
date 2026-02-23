from qaai_system.strategy_factory.generators.param_grid import generate_param_grid
from qaai_system.strategy_factory.generators.regime_profiles import REGIME_PROFILES


def test_param_grid_generation():
    params = REGIME_PROFILES["trend"]

    specs = generate_param_grid(
        family="trend-follow",
        timeframe="5m",
        regime="trend",
        params=params,
    )

    assert specs
    assert all(s.family == "trend-follow" for s in specs)
