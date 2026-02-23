from __future__ import annotations

from decimal import Decimal
import pytest

from core.strategy_factory.promotion.promotion_intelligence import (
    PromotionIntelligence,
)
from core.strategy_factory.promotion.promotion_intelligence_replay import (
    PromotionIntelligenceReplayVerifier,
)
from core.strategy_factory.promotion.promotion_intelligence_exceptions import (
    PromotionIntelligenceReplayMismatch,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

class DummyStrategySnapshot:
    def __init__(self):
        self.ssr = Decimal("0.85")
        self.drawdown = Decimal("0.05")
        self.state = "PAPER"


class DummyCapitalSnapshot:
    def __init__(self):
        self.utilization = Decimal("0.40")


class DummyScreeningSnapshot:
    def __init__(self):
        self.score = Decimal("0.75")


class DummyGovernanceSnapshot:
    def __init__(self):
        self.freeze = False


def _build_inputs():
    return dict(
        strategy_snapshot=DummyStrategySnapshot(),
        capital_snapshot=DummyCapitalSnapshot(),
        screening_snapshot=DummyScreeningSnapshot(),
        governance_snapshot=DummyGovernanceSnapshot(),
    )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_replay_success():
    intelligence = PromotionIntelligence()
    verifier = PromotionIntelligenceReplayVerifier(
        intelligence=intelligence
    )

    inputs = _build_inputs()

    # Run once to get expected hash
    decision = intelligence.evaluate(**inputs)
    expected_hash = decision.trace.trace_hash

    assert verifier.verify(
        expected_trace_hash=expected_hash,
        **inputs,
    ) is True


def test_replay_detects_mismatch():
    intelligence = PromotionIntelligence()
    verifier = PromotionIntelligenceReplayVerifier(
        intelligence=intelligence
    )

    inputs = _build_inputs()

    with pytest.raises(PromotionIntelligenceReplayMismatch):
        verifier.verify(
            expected_trace_hash="invalid_hash",
            **inputs,
        )


def test_replay_deterministic():
    intelligence = PromotionIntelligence()
    verifier = PromotionIntelligenceReplayVerifier(
        intelligence=intelligence
    )

    inputs = _build_inputs()

    trace1 = verifier.replay(**inputs)
    trace2 = verifier.replay(**inputs)

    assert trace1.trace_hash == trace2.trace_hash