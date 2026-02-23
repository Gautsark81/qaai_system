from datetime import datetime

from core.capital.usage_ledger.ledger import CapitalUsageLedger
from core.capital.coordination.coordinator import CapitalCoordinator
from core.capital.coordination.models import CapitalRequest
from core.explainability.coordination_explainer import CoordinationExplainer


def test_coordination_explanation_is_human_readable():
    ledger = CapitalUsageLedger()
    ledger.record_allocation("A", 60_000, datetime.utcnow(), "alloc")

    coordinator = CapitalCoordinator(total_capital=100_000)

    reqs = [
        CapitalRequest("B", 50_000, datetime.utcnow()),
    ]

    decision = coordinator.coordinate(reqs, ledger)

    explainer = CoordinationExplainer()

    explanation = explainer.explain(decision)

    assert "requested 50000" in explanation
    assert "granted 40000" in explanation
    assert "capital constraint" in explanation.lower()
