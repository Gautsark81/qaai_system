import pytest

from core.live_verification.execution_trace_collector import ExecutionTraceCollector
from core.live_verification.live_proof_artifact import LiveProofBuilder
from core.live_verification.proof_registry import LiveProofRegistry


def test_live_proof_is_deterministic():
    collector = ExecutionTraceCollector()
    builder = LiveProofBuilder()

    trace = collector.collect(
        strategy_dna="STRAT_X",
        capital_decision={"fraction": 0.1},
        risk_verdict={"passed": True},
        execution_intent={"symbol": "NIFTY"},
        router_call_payload={"order_id": "1"},
        mode="SHADOW",
    )

    artifact1 = builder.build(trace)
    artifact2 = builder.build(trace)

    assert artifact1.chain_hash == artifact2.chain_hash
    assert artifact1.fingerprint() == artifact2.fingerprint()


def test_registry_is_append_only():
    collector = ExecutionTraceCollector()
    builder = LiveProofBuilder()
    registry = LiveProofRegistry()

    trace = collector.collect(
        strategy_dna="STRAT_X",
        capital_decision={"fraction": 0.2},
        risk_verdict={"passed": True},
        execution_intent={"symbol": "BANKNIFTY"},
        router_call_payload={"order_id": "2"},
        mode="LIVE",
    )

    artifact = builder.build(trace)
    registry.append(artifact)

    items = registry.list()
    assert len(items) == 1
    assert items[0].authority_validated is True


def test_invalid_mode_fails_authority():
    collector = ExecutionTraceCollector()
    builder = LiveProofBuilder()

    trace = collector.collect(
        strategy_dna="STRAT_X",
        capital_decision={"fraction": 0.2},
        risk_verdict={"passed": True},
        execution_intent={"symbol": "BANKNIFTY"},
        router_call_payload={"order_id": "2"},
        mode="INVALID",
    )

    artifact = builder.build(trace)
    assert artifact.authority_validated is False