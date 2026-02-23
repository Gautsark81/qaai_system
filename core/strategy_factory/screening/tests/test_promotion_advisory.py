from decimal import Decimal

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.promotion_advisory import (
    PromotionAdvisoryAdapter,
)


def _build_screening_result():
    engine = ScreeningEngine()
    return engine.screen(
        {
            "A": Decimal("3"),
            "B": Decimal("2"),
            "C": Decimal("1"),
        }
    )


# ------------------------------------------------------------
# Contract
# ------------------------------------------------------------

def test_promotion_advisory_contract():
    result = _build_screening_result()

    adapter = PromotionAdvisoryAdapter(
        top_n_for_paper=2,
        live_rank_threshold=1,
    )

    advisory = adapter.build(screening_result=result)

    assert advisory.base_state_hash == result.state_hash
    assert advisory.ranked_strategies == ("A", "B", "C")
    assert advisory.recommended_for_paper == ("A", "B")
    assert advisory.recommended_for_live == ("A",)


# ------------------------------------------------------------
# Determinism
# ------------------------------------------------------------

def test_promotion_advisory_deterministic():
    result1 = _build_screening_result()
    result2 = _build_screening_result()

    adapter = PromotionAdvisoryAdapter()

    advisory1 = adapter.build(screening_result=result1)
    advisory2 = adapter.build(screening_result=result2)

    assert advisory1 == advisory2


# ------------------------------------------------------------
# No authority mutation
# ------------------------------------------------------------

def test_promotion_advisory_is_advisory_only():
    result = _build_screening_result()

    adapter = PromotionAdvisoryAdapter()

    advisory = adapter.build(screening_result=result)

    # Ensure original screening result unchanged
    assert result.scores[0].strategy_dna == "A"
    assert advisory.base_state_hash == result.state_hash