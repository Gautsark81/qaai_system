from core.shadow.divergence.engine import ShadowDivergenceEngine
from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import CapitalExpectation, CapitalReality


def test_capital_drift_detected():
    engine = ShadowDivergenceEngine(
        config=ShadowDivergenceConfig(
            enable_shadow_divergence=True,
            max_capital_drift_pct=1.0,
        )
    )

    expected = CapitalExpectation(expected_capital=1_000_000)
    reality = CapitalReality(actual_capital=980_000)

    report = engine.evaluate_capital(
        expectation=expected,
        reality=reality,
    )

    assert report.has_divergence is True
    assert "capital_drift" in report.reasons
