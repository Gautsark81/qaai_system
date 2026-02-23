from core.institutional_memory import (
    InstitutionalMemoryRecord,
    build_institutional_memory_snapshot,
)


def test_institutional_memory_consolidation():
    records = [
        InstitutionalMemoryRecord("strategy_aging", {"s1": 120}),
        InstitutionalMemoryRecord("governance_drift", {"threshold_changed": True}),
        InstitutionalMemoryRecord("capital_posture", {"allocated": 1_000_000}),
    ]

    snapshot = build_institutional_memory_snapshot(records)

    assert len(snapshot.memory.records) == 3
    assert snapshot.memory.checksum == snapshot.snapshot_version
