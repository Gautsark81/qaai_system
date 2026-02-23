from core.institutional_memory import (
    InstitutionalMemoryRecord,
    build_institutional_memory_snapshot,
)


def test_snapshot_is_deterministic():
    records = [
        InstitutionalMemoryRecord("stress", {"loss": 5000}),
    ]

    r1 = build_institutional_memory_snapshot(records)
    r2 = build_institutional_memory_snapshot(records)

    assert r1.snapshot_version == r2.snapshot_version
    assert r1.memory == r2.memory
