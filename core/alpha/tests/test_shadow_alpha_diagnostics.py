from core.execution.execution_mode import ExecutionMode
from core.execution.execute import execute_signal
from core.alpha.shadow_diagnostics import analyze_shadow_alpha


def test_shadow_alpha_diagnostics_are_pure_and_observational():
    """
    Shadow Alpha Diagnostics must:
    - Observe execution
    - Produce diagnostics
    - NOT affect execution intent
    """

    signal = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "quantity": 10,
        "strategy_id": "strat-alpha-1",
    }

    intent = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )

    diagnostics = analyze_shadow_alpha(
        signal=signal,
        intent=intent,
    )

    # Diagnostics object shape
    assert diagnostics.confidence_score >= 0.0
    assert diagnostics.confidence_score <= 1.0

    assert diagnostics.signal_quality in {
        "STRONG",
        "MODERATE",
        "WEAK",
    }

    assert diagnostics.regime_tag is not None
    assert isinstance(diagnostics.feature_attribution, dict)

    assert diagnostics.probability_estimate >= 0.0
    assert diagnostics.probability_estimate <= 1.0

    assert isinstance(diagnostics.explanation, str)

    # HARD LAW: diagnostics must not alter execution
    intent_after = execute_signal(
        signal=signal,
        mode=ExecutionMode.SHADOW,
    )

    assert intent == intent_after
