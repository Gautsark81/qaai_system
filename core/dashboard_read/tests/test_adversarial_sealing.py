import json
import pytest
from pathlib import Path
from datetime import datetime, timezone

from core.dashboard_read.snapshot import SystemSnapshot
from core.dashboard_read.evidence.record import EvidenceRecord
from core.dashboard_read.persistence import snapshot_to_json, snapshot_from_json
from core.dashboard_read.persistence.load import load_evidence_record
from core.dashboard_read.verification.verifier import (
    verify_evidence_record,
    verify_evidence_chain,
)


def _build_snapshot() -> SystemSnapshot:
    """
    Build a fully valid SystemSnapshot using the ONLY
    supported offline construction path: from_dict.

    All domain invariants are satisfied.
    No providers are touched.
    """

    payload = {
        "meta": {
            "snapshot_id": "TEST_SNAPSHOT",
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "execution_mode": "offline",
            "market_status": "CLOSED",
            "system_version": "test-1.0.0",
            "schema_version": 1,
        },
        "market_state": {},
        "system_health": {
            "data_feeds": [],
            "broker": {
                "last_heartbeat": None,
                "latency_ms": None,
            },
            "services": {},
            "alerts_active": False,
        },
        "pipeline_state": {},
        "strategy_state": {},
        "execution_state": {},
        "risk_state": {},
        "capital_state": {},
        "shadow_state": {},
        "paper_state": {},
        "ops_state": {},
        "incidents": [],
        "compliance": {},
    }

    return SystemSnapshot.from_dict(payload)


def test_bit_flip_detection():
    snap = _build_snapshot()
    blob = snapshot_to_json(snap)

    payload = json.loads(blob)
    payload["snapshot"]["meta"]["execution_mode"] = "CORRUPTED"

    tampered_blob = json.dumps(payload)
    snap2 = snapshot_from_json(tampered_blob)

    assert snap.meta.fingerprint != snap2.meta.fingerprint


def test_sealed_evidence_detects_snapshot_tampering(tmp_path: Path):
    snap = _build_snapshot()
    path = tmp_path / "evidence.json"

    snapshot_to_json(snap, path=path)

    raw = json.loads(path.read_text())
    raw["snapshot"]["meta"]["execution_mode"] = "CORRUPTED"
    path.write_text(json.dumps(raw))

    with pytest.raises(Exception):
        load_evidence_record(path)


def test_chain_truncation_detected():
    s1 = _build_snapshot()
    s2 = _build_snapshot()

    r1 = EvidenceRecord.create(s1.to_dict())
    r2 = EvidenceRecord.create(
        s2.to_dict(),
        previous_chain_hash=r1.chain_hash,
    )

    report = verify_evidence_chain([r2])
    assert not report.is_valid


def test_chain_reordering_detected():
    s1 = _build_snapshot()
    s2 = _build_snapshot()

    r1 = EvidenceRecord.create(s1.to_dict())
    r2 = EvidenceRecord.create(
        s2.to_dict(),
        previous_chain_hash=r1.chain_hash,
    )

    report = verify_evidence_chain([r2, r1])
    assert not report.is_valid


def test_forged_previous_chain_hash_detected():
    snap = _build_snapshot()

    record = EvidenceRecord.create(
        snap.to_dict(),
        previous_chain_hash="f" * 64,
    )

    report = verify_evidence_record(record)
    assert not report.is_valid


def test_metadata_forgery_does_not_affect_hashes():
    snap = _build_snapshot()

    r1 = EvidenceRecord.create(snap.to_dict(), producer_id="alpha")
    r2 = EvidenceRecord.create(snap.to_dict(), producer_id="beta")

    assert r1.snapshot_hash == r2.snapshot_hash
    assert r1.chain_hash == r2.chain_hash


def test_replay_with_modified_history_detected():
    """
    A valid replay must preserve exact lineage.

    This test simulates a true history-modification attack:
    The second record is rebuilt to reference a forged parent,
    breaking deterministic parent linkage.

    Reconstructing an identical genesis record is NOT an attack
    in a content-addressed deterministic system.
    """

    s1 = _build_snapshot()
    s2 = _build_snapshot()

    # Legitimate chain
    r1 = EvidenceRecord.create(s1.to_dict())
    r2 = EvidenceRecord.create(
        s2.to_dict(),
        previous_chain_hash=r1.chain_hash,
    )

    # ---- ATTACK ----
    # Forge parent reference for r2 (history substitution attack)
    forged_parent_hash = "f" * 64

    forged_r2 = EvidenceRecord.create(
        s2.to_dict(),
        previous_chain_hash=forged_parent_hash,
    )

    # Chain now contains invalid lineage
    report = verify_evidence_chain([r1, forged_r2])

    assert not report.is_valid


def test_mixed_sealed_and_unsealed_rejected(tmp_path: Path):
    snap = _build_snapshot()
    path = tmp_path / "evidence.json"

    snapshot_to_json(snap, path=path)
    raw_snapshot_blob = snapshot_to_json(snap)

    with pytest.raises(Exception):
        load_evidence_record(raw_snapshot_blob)  # type: ignore
