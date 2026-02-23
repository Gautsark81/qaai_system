# core/governance/tests/test_phase14_governance_integrity_hashing.py

from datetime import datetime, timezone

from core.governance.integrity.governance_snapshot_hash_engine import (
    GovernanceSnapshotHashEngine,
)
from core.governance.integrity.governance_ledger_fingerprint_engine import (
    GovernanceLedgerFingerprintEngine,
)
from core.governance.integrity.governance_proof_artifact import (
    GovernanceProofEngine,
)
from core.governance.reconstruction import GovernanceState


def _build_state():
    return GovernanceState(
        governance_id="gov-int-001",
        strategy_id="STRAT-1",
        final_capital=1_000_000,
        capital_scale_factor=1.0,
        capital_scale_reason="BASE",
        throttle_level=1.0,
        throttle_factor=1.0,
        throttle_reason="NONE",
        last_updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


# ============================================================
# Snapshot Hash Determinism
# ============================================================


def test_snapshot_hash_is_deterministic():
    state1 = _build_state()
    state2 = _build_state()

    h1 = GovernanceSnapshotHashEngine.compute_hash(state1)
    h2 = GovernanceSnapshotHashEngine.compute_hash(state2)

    assert h1 == h2


def test_snapshot_hash_changes_on_mutation():
    state1 = _build_state()
    state2 = _build_state()

    state2 = GovernanceState(
        governance_id=state2.governance_id,
        strategy_id=state2.strategy_id,
        final_capital=900_000,  # changed
        capital_scale_factor=1.0,
        capital_scale_reason="BASE",
        throttle_level=1.0,
        throttle_factor=1.0,
        throttle_reason="NONE",
        last_updated_at=state2.last_updated_at,
    )

    h1 = GovernanceSnapshotHashEngine.compute_hash(state1)
    h2 = GovernanceSnapshotHashEngine.compute_hash(state2)

    assert h1 != h2


# ============================================================
# Ledger Fingerprint Determinism
# ============================================================


def test_ledger_fingerprint_is_order_independent():
    ledger_a = [
        {"a": 1, "b": 2},
        {"x": 3, "y": 4},
    ]

    ledger_b = [
        {"x": 3, "y": 4},
        {"a": 1, "b": 2},
    ]

    f1 = GovernanceLedgerFingerprintEngine.compute_fingerprint(ledgers=ledger_a)
    f2 = GovernanceLedgerFingerprintEngine.compute_fingerprint(ledgers=ledger_b)

    assert f1 == f2


# ============================================================
# Combined Governance Proof
# ============================================================


def test_governance_proof_combined_hash_deterministic():
    state = _build_state()

    ledgers = [
        {"entry": 1},
        {"entry": 2},
    ]

    proof1 = GovernanceProofEngine.generate_proof(
        state=state,
        ledgers=ledgers,
    )

    proof2 = GovernanceProofEngine.generate_proof(
        state=state,
        ledgers=ledgers,
    )

    assert proof1.snapshot_hash == proof2.snapshot_hash
    assert proof1.ledger_hash == proof2.ledger_hash
    assert proof1.combined_hash == proof2.combined_hash


def test_governance_proof_changes_if_ledger_changes():
    state = _build_state()

    ledgers_a = [
        {"entry": 1},
        {"entry": 2},
    ]

    ledgers_b = [
        {"entry": 1},
        {"entry": 999},  # changed
    ]

    proof1 = GovernanceProofEngine.generate_proof(
        state=state,
        ledgers=ledgers_a,
    )

    proof2 = GovernanceProofEngine.generate_proof(
        state=state,
        ledgers=ledgers_b,
    )

    assert proof1.combined_hash != proof2.combined_hash


# ============================================================
# Replay Determinism
# ============================================================


def test_replay_reconstruction_produces_same_hash():
    state = _build_state()

    h1 = GovernanceSnapshotHashEngine.compute_hash(state)
    h2 = GovernanceSnapshotHashEngine.compute_hash(state)

    assert h1 == h2