import pytest

from core.v2.intelligence.strategy_scoring import (
    StrategyAlphaScorer,
    AlphaScore,
)


def test_strong_alpha_score():
    scorer = StrategyAlphaScorer()

    result = scorer.score(
        strategy_id="S1",
        ssr=0.9,
        health=0.85,
        regime_fit=0.8,
        stability=0.1,
    )

    assert isinstance(result, AlphaScore)
    assert result.verdict == "STRONG_ALPHA"
    assert result.score > 0.75
    assert "stability_penalty" in result.components


def test_moderate_alpha_score():
    scorer = StrategyAlphaScorer()

    result = scorer.score(
        strategy_id="S2",
        ssr=0.6,
        health=0.6,
        regime_fit=0.55,
        stability=0.2,
    )

    assert result.verdict == "MODERATE_ALPHA"


def test_weak_alpha_score():
    scorer = StrategyAlphaScorer()

    result = scorer.score(
        strategy_id="S3",
        ssr=0.45,
        health=0.4,
        regime_fit=0.4,
        stability=0.3,
    )

    assert result.verdict == "WEAK_ALPHA"


def test_no_alpha_score():
    scorer = StrategyAlphaScorer()

    result = scorer.score(
        strategy_id="S4",
        ssr=0.2,
        health=0.2,
        regime_fit=0.1,
        stability=0.5,
    )

    assert result.verdict == "NO_ALPHA"


def test_invalid_inputs_raise():
    scorer = StrategyAlphaScorer()

    with pytest.raises(ValueError):
        scorer.score(
            strategy_id="BAD",
            ssr=1.2,
            health=0.5,
            regime_fit=0.5,
            stability=0.5,
        )
