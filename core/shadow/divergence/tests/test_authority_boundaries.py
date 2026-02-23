from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import SignalSnapshot, FillSnapshot


def test_divergence_engine_has_no_execution_or_capital_authority():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig(enable_shadow_divergence=True)
    )

    signal = SignalSnapshot(
        symbol="AXISBANK",
        side="BUY",
        quantity=1,
        price=1000.0,
    )

    fill = FillSnapshot(
        symbol="AXISBANK",
        side="BUY",
        quantity=1,
        avg_price=1000.0,
    )

    report = engine.evaluate(signal, fill)

    assert report.has_execution_authority is False
    assert report.has_capital_authority is False
