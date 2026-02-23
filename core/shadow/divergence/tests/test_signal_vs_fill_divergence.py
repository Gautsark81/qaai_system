from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import (
    SignalSnapshot,
    FillSnapshot,
)


def test_no_divergence_when_signal_matches_fill():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig(enable_shadow_divergence=True)
    )

    signal = SignalSnapshot(
        symbol="RELIANCE",
        side="BUY",
        quantity=100,
        price=2500.0,
    )

    fill = FillSnapshot(
        symbol="RELIANCE",
        side="BUY",
        quantity=100,
        avg_price=2500.0,
    )

    report = engine.evaluate(signal=signal, fill=fill)

    assert report.has_divergence is False
    assert report.reasons == []
