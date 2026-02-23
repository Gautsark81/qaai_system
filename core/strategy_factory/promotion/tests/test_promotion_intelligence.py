from decimal import Decimal

from core.strategy_factory.promotion.promotion_intelligence import (
    PromotionIntelligenceEngine,
)


def test_promotion_intelligence_contract():
    engine = PromotionIntelligenceEngine()

    artifact = engine.score(
        strategy_dna="STRAT_X",
        ssr_strength=Decimal("0.9"),
        regime_alignment=Decimal("0.8"),
        capital_fit=Decimal("0.7"),
        governance_health=Decimal("1.0"),
    )

    assert artifact.strategy_dna == "STRAT_X"
    assert artifact.total_score > Decimal("0")
    assert artifact.state_hash is not None
    assert len(artifact.components) == 4


def test_promotion_intelligence_determinism():
    engine = PromotionIntelligenceEngine()

    inputs = dict(
        strategy_dna="STRAT_X",
        ssr_strength=Decimal("0.9"),
        regime_alignment=Decimal("0.8"),
        capital_fit=Decimal("0.7"),
        governance_health=Decimal("1.0"),
    )

    a1 = engine.score(**inputs)
    a2 = engine.score(**inputs)

    assert a1.state_hash == a2.state_hash
    assert a1.total_score == a2.total_score


def test_promotion_intelligence_no_authority():
    engine = PromotionIntelligenceEngine()

    artifact = engine.score(
        strategy_dna="STRAT_X",
        ssr_strength=Decimal("1.0"),
        regime_alignment=Decimal("1.0"),
        capital_fit=Decimal("1.0"),
        governance_health=Decimal("1.0"),
    )

    # Ensure it does not expose any mutation fields
    assert not hasattr(artifact, "promote")
    assert not hasattr(artifact, "execute")
    assert not hasattr(artifact, "apply")