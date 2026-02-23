# core/capital/tests/test_capital_evidence_emission.py

from core.capital.allocation.allocator import PortfolioCapitalAllocator
from core.capital.capital_contracts import StrategyCapitalSignal
from core.evidence.decision_store import DecisionEvidenceStore


def test_capital_allocator_emits_evidence_without_affecting_weights():
    allocator = PortfolioCapitalAllocator()
    store = DecisionEvidenceStore()

    signals = {
        "alpha_1": StrategyCapitalSignal(ssr=0.8, confidence=0.9, regime_score=0.95),
        "alpha_2": StrategyCapitalSignal(ssr=0.6, confidence=0.7, regime_score=0.8),
    }

    weights = allocator.allocate(
        signals=signals,
        min_weight=0.0,
        evidence_store=store,
    )

    # Allocation correctness
    assert abs(sum(weights.values()) - 1.0) < 1e-6

    # Evidence correctness
    records = store.all()
    assert len(records) == 2

    strategy_ids = {e.strategy_id for e in records}
    assert strategy_ids == {"alpha_1", "alpha_2"}


def test_allocator_works_without_evidence_store():
    allocator = PortfolioCapitalAllocator()

    signals = {
        "alpha_1": StrategyCapitalSignal(ssr=0.5, confidence=0.5, regime_score=0.5),
    }

    weights = allocator.allocate(signals=signals)

    assert weights["alpha_1"] == 1.0

def test_capital_evidence_contains_attribution_fields():
    allocator = PortfolioCapitalAllocator()
    store = DecisionEvidenceStore()

    signals = {
        "alpha": StrategyCapitalSignal(ssr=0.9, confidence=0.8, regime_score=0.9),
    }

    allocator.allocate(signals=signals, evidence_store=store)

    record = store.all()[0]
    factor_keys = {k for k, _ in record.factors}

    assert "strategy_id" in factor_keys
