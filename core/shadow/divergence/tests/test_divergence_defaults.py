from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig


def test_divergence_engine_disabled_by_default():
    engine = ShadowDivergenceEngine()
    assert engine.is_enabled is False


def test_divergence_engine_requires_explicit_enable():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig()
    )
    assert engine.is_enabled is False


def test_divergence_engine_enables_with_flag():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig(enable_shadow_divergence=True)
    )
    assert engine.is_enabled is True
