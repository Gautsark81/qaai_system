from datetime import datetime

from core.capital.usage_ledger.ledger import CapitalUsageLedger
from core.explainability.capital_explainer import CapitalExplainer


def test_capital_explanation_contains_full_breakdown():
    ledger = CapitalUsageLedger()
    ledger.record_allocation("A", 100_000, datetime.utcnow(), "alloc")
    ledger.record_consumption("A", 40_000, datetime.utcnow(), "trade")

    explainer = CapitalExplainer()

    explanation = explainer.explain(ledger)

    assert "Strategy A" in explanation
    assert "Allocated: 100000" in explanation
    assert "Consumed: 40000" in explanation
    assert "Used Capital: 40000" in explanation
