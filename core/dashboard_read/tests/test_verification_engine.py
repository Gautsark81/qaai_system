# core/dashboard_read/tests/test_verification_engine.py

from core.dashboard_read.evidence.record import EvidenceRecord
from core.dashboard_read.verification.verifier import (
    verify_evidence_record,
    verify_evidence_chain,
)


def test_valid_single_record_passes():
    snapshot = {"a": 1}
    record = EvidenceRecord.create(snapshot)

    report = verify_evidence_record(record)

    assert report.is_valid
    assert report.issues == []


def test_tampered_snapshot_detected():
    snapshot = {"a": 1}
    record = EvidenceRecord.create(snapshot)

    # Tamper with snapshot
    object.__setattr__(record, "snapshot", {"a": 999})

    report = verify_evidence_record(record)

    assert not report.is_valid
    assert any("SNAPSHOT_HASH_MISMATCH" in i.code for i in report.issues)


def test_valid_chain_passes():
    r1 = EvidenceRecord.create({"a": 1})
    r2 = EvidenceRecord.create({"a": 2}, previous_chain_hash=r1.chain_hash)

    report = verify_evidence_chain([r1, r2])

    assert report.is_valid


def test_chain_link_break_detected():
    r1 = EvidenceRecord.create({"a": 1})
    r2 = EvidenceRecord.create({"a": 2})  # wrong previous hash

    report = verify_evidence_chain([r1, r2])

    assert not report.is_valid
    assert any("CHAIN_LINK_BROKEN" in i.code for i in report.issues)


def test_reordering_detected():
    r1 = EvidenceRecord.create({"a": 1})
    r2 = EvidenceRecord.create({"a": 2}, previous_chain_hash=r1.chain_hash)

    report = verify_evidence_chain([r2, r1])

    assert not report.is_valid
