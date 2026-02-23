from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import SignalSnapshot, FillSnapshot


def test_divergence_engine_replayable():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig(enable_shadow_divergence=True)
    )

    signal = SignalSnapshot(
        symbol="SBIN",
        side="BUY",
        quantity=100,
        price=600.0,
    )

    fill = FillSnapshot(
        symbol="SBIN",
        side="BUY",
        quantity=100,
        avg_price=600.0,
    )

    r1 = engine.evaluate(signal, fill)
    r2 = engine.evaluate(signal, fill)

    assert r1 == r2
