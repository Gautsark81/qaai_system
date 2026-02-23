from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import SignalSnapshot, FillSnapshot
from core.governance.reconstruction import reconstruct_system_state


def test_divergence_engine_has_no_side_effects():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig(enable_shadow_divergence=True)
    )

    signal = SignalSnapshot(
        symbol="ITC",
        side="BUY",
        quantity=10,
        price=450.0,
    )

    fill = FillSnapshot(
        symbol="ITC",
        side="BUY",
        quantity=10,
        avg_price=450.0,
    )

    before = reconstruct_system_state()
    engine.evaluate(signal, fill)
    after = reconstruct_system_state()

    assert before == after
