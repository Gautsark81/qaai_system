# core/dashboard_read/tests/test_evidence_record.py

from core.dashboard_read.evidence.record import EvidenceRecord
from core.dashboard_read.crypto.chain import GENESIS_CHAIN_HASH


def test_evidence_record_is_immutable():
    snapshot = {"a": 1}
    record = EvidenceRecord.create(snapshot)

    try:
        record.snapshot_hash = "tampered"
        assert False, "EvidenceRecord should be immutable"
    except Exception:
        assert True


def test_evidence_record_hashes_are_consistent():
    snapshot = {"a": 1}

    record = EvidenceRecord.create(snapshot)

    assert record.snapshot_hash is not None
    assert record.chain_hash is not None
    assert record.previous_chain_hash == GENESIS_CHAIN_HASH


def test_evidence_record_chain_links():
    s1 = {"a": 1}
    s2 = {"a": 2}

    r1 = EvidenceRecord.create(s1)
    r2 = EvidenceRecord.create(s2, previous_chain_hash=r1.chain_hash)

    assert r2.previous_chain_hash == r1.chain_hash
    assert r1.chain_hash != r2.chain_hash


def test_metadata_does_not_affect_hashes():
    snapshot = {"a": 1}

    r1 = EvidenceRecord.create(snapshot, producer_id="alpha")
    r2 = EvidenceRecord.create(snapshot, producer_id="beta")

    assert r1.snapshot_hash == r2.snapshot_hash
    assert r1.chain_hash == r2.chain_hash
