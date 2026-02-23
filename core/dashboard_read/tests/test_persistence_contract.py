# core/dashboard_read/tests/test_persistence_contract.py

import json
import pytest
from pathlib import Path

from core.dashboard_read.evidence.record import EvidenceRecord
from core.dashboard_read.persistence.store import (
    store_evidence_record,
    PersistenceError,
)
from core.dashboard_read.persistence.load import load_evidence_record


def test_store_and_load_roundtrip(tmp_path: Path):
    snapshot = {"a": 1}
    record = EvidenceRecord.create(snapshot)

    path = tmp_path / "evidence.json"

    store_evidence_record(record, path)
    loaded = load_evidence_record(path)

    assert loaded == record


def test_rejects_non_evidence_record(tmp_path: Path):
    path = tmp_path / "bad.json"

    with pytest.raises(PersistenceError):
        store_evidence_record({"a": 1}, path)  # type: ignore


def test_detects_tampering_on_load(tmp_path: Path):
    snapshot = {"a": 1}
    record = EvidenceRecord.create(snapshot)

    path = tmp_path / "evidence.json"
    store_evidence_record(record, path)

    # Tamper with stored snapshot
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["snapshot"]["a"] = 999
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(PersistenceError):
        load_evidence_record(path)
