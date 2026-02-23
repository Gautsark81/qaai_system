from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import SignalSnapshot, FillSnapshot


def test_divergence_engine_deterministic():
    config = ShadowDivergenceConfig(enable_shadow_divergence=True)

    engine_1 = ShadowDivergenceEngine(config=config)
    engine_2 = ShadowDivergenceEngine(config=config)

    signal = SignalSnapshot(
        symbol="HDFCBANK",
        side="BUY",
        quantity=10,
        price=1600.0,
    )

    fill = FillSnapshot(
        symbol="HDFCBANK",
        side="BUY",
        quantity=10,
        avg_price=1600.0,
    )

    assert engine_1.evaluate(signal, fill) == engine_2.evaluate(signal, fill)
