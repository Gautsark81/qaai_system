import pytest

from core.capital.capital_allocator import (
    CapitalDecisionEngine,
    CapitalDecision,
)
from core.regime.taxonomy import MarketRegime
from core.regime.health import StrategyHealth
from core.regime.confidence import RegimeConfidencePolicy


# ======================================================
# Test Fixtures (Minimal, Explicit)
# ======================================================

class DummySpec:
    def __init__(self, allowed_regimes=None):
        self.allowed_regimes = allowed_regimes or set()


class DummyRecord:
    def __init__(self, dna="alpha_1", state="PAPER", allowed_regimes=None):
        self.dna = dna
        self.state = state
        self.spec = DummySpec(allowed_regimes=allowed_regimes)


class DummyCapitalGuard:
    def allocate(self, order_value: float):
        return None  # no-op guard


@pytest.fixture
def regime_policy():
    return RegimeConfidencePolicy(
        multipliers={
            MarketRegime.TREND_LOW_VOL: 1.0,
            MarketRegime.RANGE_HIGH_VOL: 0.8,
            MarketRegime.CHAOTIC: 0.0,
        }
    )


@pytest.fixture
def engine(regime_policy):
    return CapitalDecisionEngine(
        regime_confidence_policy=regime_policy,
        hard_capital_guard=DummyCapitalGuard(),
    )


# ======================================================
# Helper
# ======================================================

def make_health(ssr: float) -> StrategyHealth:
    h = StrategyHealth()
    successes = int(ssr * 10)
    failures = 10 - successes

    for _ in range(successes):
        h.record_outcome(
            regime=MarketRegime.TREND_LOW_VOL,
            success=True,
        )

    for _ in range(failures):
        h.record_outcome(
            regime=MarketRegime.TREND_LOW_VOL,
            success=False,
        )

    return h


# ======================================================
# HARD GATES
# ======================================================

def test_block_if_not_promoted(engine):
    record = DummyRecord(state="BACKTESTED")
    health = make_health(0.9)

    result = engine.decide(
        record=record,
        health=health,
        confidence=0.9,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert result.decision == CapitalDecision.BLOCK
    assert "not promoted" in result.reasons[0]


def test_block_if_no_health(engine):
    record = DummyRecord()

    result = engine.decide(
        record=record,
        health=None,
        confidence=0.8,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert result.decision == CapitalDecision.BLOCK
    assert "No SSR data" in result.reasons[0]


def test_block_if_ssr_below_min(engine):
    record = DummyRecord()
    health = make_health(0.30)

    result = engine.decide(
        record=record,
        health=health,
        confidence=1.0,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert result.decision == CapitalDecision.BLOCK
    assert "SSR below minimum" in result.reasons[0]


# ======================================================
# REGIME COMPATIBILITY
# ======================================================

def test_block_if_regime_incompatible_and_weak_ssr(engine):
    record = DummyRecord(
        allowed_regimes={MarketRegime.TREND_LOW_VOL}
    )
    health = make_health(0.60)

    result = engine.decide(
        record=record,
        health=health,
        confidence=1.0,
        regime=MarketRegime.RANGE_HIGH_VOL,
    )

    assert result.decision == CapitalDecision.BLOCK
    assert "Regime incompatible" in result.reasons[0]


def test_reduce_if_regime_incompatible_but_strong_ssr(engine):
    record = DummyRecord(
        allowed_regimes={MarketRegime.TREND_LOW_VOL}
    )
    health = make_health(0.80)

    result = engine.decide(
        record=record,
        health=health,
        confidence=1.0,
        regime=MarketRegime.RANGE_HIGH_VOL,
    )

    assert result.decision == CapitalDecision.REDUCE
    assert any("SSR strong" in r for r in result.reasons)


# ======================================================
# CONFIDENCE & REGIME MULTIPLIERS
# ======================================================

def test_block_if_regime_chaotic(engine):
    record = DummyRecord()
    health = make_health(0.9)

    result = engine.decide(
        record=record,
        health=health,
        confidence=1.0,
        regime=MarketRegime.CHAOTIC,
    )

    assert result.decision == CapitalDecision.BLOCK
    assert "Regime chaotic" in result.reasons[0]


def test_confidence_scales_but_does_not_override(engine):
    record = DummyRecord()
    health = make_health(0.60)

    result = engine.decide(
        record=record,
        health=health,
        confidence=0.2,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert result.decision == CapitalDecision.REDUCE
    assert result.multiplier < 0.6
    assert any("Confidence" in r for r in result.reasons)


# ======================================================
# RISK DOMINANCE
# ======================================================

def test_risk_cap_dominates(engine):
    record = DummyRecord()
    health = make_health(0.90)

    result = engine.decide(
        record=record,
        health=health,
        confidence=1.0,
        regime=MarketRegime.TREND_LOW_VOL,
        risk_cap=0.25,
    )

    assert result.decision == CapitalDecision.REDUCE
    assert result.multiplier == 0.25
    assert any("Risk cap applied" in r for r in result.reasons)


def test_risk_block_zero(engine):
    record = DummyRecord()
    health = make_health(0.95)

    result = engine.decide(
        record=record,
        health=health,
        confidence=1.0,
        regime=MarketRegime.TREND_LOW_VOL,
        risk_cap=0.0,
    )

    assert result.decision == CapitalDecision.BLOCK
    assert "Risk block" in result.reasons[0]


# ======================================================
# ALLOW PATH
# ======================================================

def test_allow_high_ssr_high_confidence(engine):
    record = DummyRecord()
    health = make_health(0.95)

    result = engine.decide(
        record=record,
        health=health,
        confidence=1.0,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert result.decision == CapitalDecision.ALLOW
    assert result.multiplier == 1.0


# ======================================================
# EXPLAINABILITY CONTRACT
# ======================================================

def test_explainability_payload_complete(engine):
    record = DummyRecord()
    health = make_health(0.70)

    result = engine.decide(
        record=record,
        health=health,
        confidence=0.8,
        regime=MarketRegime.RANGE_HIGH_VOL,
    )

    assert isinstance(result.reasons, list)
    assert isinstance(result.diagnostics, dict)
    assert "ssr" in result.diagnostics
    assert "confidence" in result.diagnostics
    assert "regime" in result.diagnostics
