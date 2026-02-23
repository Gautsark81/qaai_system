from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import SignalSnapshot, FillSnapshot


def test_quantity_divergence_detected():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig(enable_shadow_divergence=True)
    )

    signal = SignalSnapshot(
        symbol="TCS",
        side="SELL",
        quantity=200,
        price=3500.0,
    )

    fill = FillSnapshot(
        symbol="TCS",
        side="SELL",
        quantity=150,
        avg_price=3500.0,
    )

    report = engine.evaluate(signal=signal, fill=fill)

    assert report.has_divergence is True
    assert "quantity_mismatch" in report.reasons
