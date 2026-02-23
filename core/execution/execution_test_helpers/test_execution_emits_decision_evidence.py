from core.execution.engine import ExecutionEngine
from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.decision_store import InMemoryDecisionStore


def test_execution_emits_exactly_one_decision_evidence():
    store = InMemoryDecisionStore()
    engine = ExecutionEngine(evidence_store=store)

    engine.execute(
        run_id="RUN-EVID-1",
        strategy_id="S1",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=100.0,
    )

    evidence = store.all()

    assert len(evidence) == 1
    assert isinstance(evidence[0], DecisionEvidence)
    assert evidence[0].decision_type == "EXECUTION"
    assert evidence[0].decision_id == "RUN-EVID-1"


def test_execution_crash_retry_does_not_duplicate_evidence():
    store = InMemoryDecisionStore()

    engine = ExecutionEngine(evidence_store=store)
    engine.execute(
        run_id="RUN-EVID-CRASH",
        strategy_id="S1",
        symbol="BANKNIFTY",
        side="BUY",
        quantity=1,
        price=100.0,
    )

    # Simulate process restart
    engine = ExecutionEngine(evidence_store=store)
    engine.execute(
        run_id="RUN-EVID-CRASH",
        strategy_id="S1",
        symbol="BANKNIFTY",
        side="BUY",
        quantity=1,
        price=100.0,
    )

    assert len(store.all()) == 1


def test_execution_replay_does_not_emit_evidence():
    store = InMemoryDecisionStore()
    engine = ExecutionEngine(evidence_store=store)

    engine.execute(
        run_id="RUN-EVID-REPLAY",
        replay=True,
        strategy_id="S1",
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=100.0,
    )

    assert store.all() == []
