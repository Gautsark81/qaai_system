from core.compliance.provenance.linker import ProvenanceLinker
from core.compliance.provenance.models import EvidenceRef, DecisionLink


def test_trade_provenance_chain_is_deterministic():
    linker = ProvenanceLinker()

    d1 = DecisionLink(
        decision_id="D2",
        decision_type="governance",
        evidence=[
            EvidenceRef(
                ref_type="timeline_event",
                ref_id="E2",
                metadata={"ts": "2026-01-02T09:05:00"},
            )
        ],
    )
    d2 = DecisionLink(
        decision_id="D1",
        decision_type="risk",
        evidence=[
            EvidenceRef(
                ref_type="timeline_event",
                ref_id="E1",
                metadata={"ts": "2026-01-02T09:00:00"},
            )
        ],
    )

    chain = linker.build_trade_chain(
        trade_id="T1",
        decision_links=[d1, d2],
    )

    assert chain.trade_id == "T1"
    assert [d.decision_id for d in chain.decisions] == ["D1", "D2"]


def test_evidence_refs_preserved():
    linker = ProvenanceLinker()

    evidence = EvidenceRef(
        ref_type="causal_node",
        ref_id="C1",
        metadata={"chain_id": "chain-1"},
    )

    decision = DecisionLink(
        decision_id="D1",
        decision_type="risk",
        evidence=[evidence],
    )

    chain = linker.build_trade_chain(
        trade_id="T9",
        decision_links=[decision],
    )

    assert chain.decisions[0].evidence[0].ref_id == "C1"
