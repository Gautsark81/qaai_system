import pytest

from core.v2.adapters.v1_readonly import V1ReadonlyAdapter
from core.v2.adapters.lifecycle_adapter import LifecycleAlphaAdapter
from core.v2.adapters.capital_adapter import CapitalAlphaAdapter
from core.v2.adapters.evidence_adapter import EvidenceAlphaAdapter
from core.v2.intelligence.strategy_scoring import StrategyAlphaScorer


# ---------------------------------------------------------
# DUMMY V1 STORE — STRICTLY READ ONLY
# ---------------------------------------------------------

class DummyV1Store:
    def get_strategy_snapshot(self, strategy_id: str):
        return {
            "strategy_id": strategy_id,
            "ssr": 0.85,
            "health": 0.9,
            "regime_fit": 0.8,
            "stability": 0.75,
            "lifecycle_state": "LIVE",
            "capital_approved": True,
        }

    # 🚨 Any mutation attempt is a hard failure
    def __getattr__(self, name):
        raise RuntimeError(f"ILLEGAL v1 MUTATION ATTEMPT: {name}")


# ---------------------------------------------------------
# v2 ISOLATION TESTS (NON-NEGOTIABLE)
# ---------------------------------------------------------

def test_v2_can_read_v1_state_only():
    store = DummyV1Store()
    adapter = V1ReadonlyAdapter(store)

    snap = adapter.snapshot_strategy("STRAT_X")

    assert snap.strategy_id == "STRAT_X"
    assert snap.ssr >= 0.8
    assert snap.lifecycle_state == "LIVE"


def test_v2_lifecycle_adapter_is_gate_only():
    adapter = LifecycleAlphaAdapter()

    assert adapter.allow_alpha("LIVE") == "ALLOW"
    assert adapter.allow_alpha("DEGRADED") == "BLOCK"
    assert adapter.allow_alpha("RETIRED") == "BLOCK"


def test_v2_capital_adapter_is_advisory_only():
    adapter = CapitalAlphaAdapter()

    assert adapter.allow_alpha(True) == "CAPITAL_OK"
    assert adapter.allow_alpha(False) == "CAPITAL_BLOCKED"


def test_v2_alpha_scoring_is_side_effect_free():
    scorer = StrategyAlphaScorer()

    result = scorer.score(
        strategy_id="STRAT_X",
        ssr=0.9,
        health=0.9,
        regime_fit=0.85,
        stability=0.8,
    )

    assert result.verdict == "STRONG_ALPHA"
    assert result.alpha_score >= 0.8


def test_v2_cannot_mutate_v1_state_under_any_condition():
    store = DummyV1Store()

    with pytest.raises(RuntimeError):
        store.promote_strategy("STRAT_X")

    with pytest.raises(RuntimeError):
        store.allocate_capital("STRAT_X", 100000)

    with pytest.raises(RuntimeError):
        store.override_governance("STRAT_X")
