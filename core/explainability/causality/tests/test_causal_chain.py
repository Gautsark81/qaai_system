from core.explainability.timeline.events import NarrativeEvent
from core.explainability.causality.builder import CausalChainBuilder


def test_causal_chain_preserves_order_and_evidence():
    events = [
        NarrativeEvent(
            "2026-01-02T09:00:00",
            "risk",
            "Risk approved",
            {"risk_id": "R1"},
        ),
        NarrativeEvent(
            "2026-01-02T09:05:00",
            "execution",
            "Trade executed",
            {"trade_id": "T1"},
        ),
    ]

    builder = CausalChainBuilder()
    chain = builder.build_chain(
        chain_id="chain-1",
        ordered_events=events,
    )

    assert len(chain.nodes) == 2
    assert chain.nodes[0].description == "Risk approved"
    assert chain.nodes[0].evidence_ref["risk_id"] == "R1"
    assert chain.nodes[1].evidence_ref["trade_id"] == "T1"
