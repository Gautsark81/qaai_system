from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import SignalSnapshot, FillSnapshot


def test_price_slippage_detected():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig(
            enable_shadow_divergence=True,
            max_price_slippage_pct=0.5,
        )
    )

    signal = SignalSnapshot(
        symbol="INFY",
        side="BUY",
        quantity=50,
        price=1500.0,
    )

    fill = FillSnapshot(
        symbol="INFY",
        side="BUY",
        quantity=50,
        avg_price=1510.0,
    )

    report = engine.evaluate(signal=signal, fill=fill)

    assert report.has_divergence is True
    assert "price_slippage" in report.reasons
