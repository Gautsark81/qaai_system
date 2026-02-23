from tests.domain.validation.test_fingerprint_validator import _valid_fingerprint
from domain.strategy_factory.strategy_governance_gate import StrategyGovernanceGate


def test_strategy_blocked_on_low_ssr():
    fp = _valid_fingerprint()

    cand = StrategyGovernanceGate.evaluate(
        strategy_id="STRAT1",
        fingerprint=fp,
        ssr=0.70,
    )

    assert cand.eligible is False
    assert "SSR" in cand.rejection_reason


def test_strategy_allowed_on_valid_ssr():
    fp = _valid_fingerprint()

    cand = StrategyGovernanceGate.evaluate(
        strategy_id="STRAT2",
        fingerprint=fp,
        ssr=0.90,
    )

    assert cand.eligible is True
    assert cand.rejection_reason is None
