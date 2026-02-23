from pathlib import Path

from core.operations.ops_events import OpsEvent
from core.operations.ops_store import OpsEventStore


def test_ops_store_append_and_load(tmp_path: Path):
    store = OpsEventStore(root_dir=tmp_path)

    ev = OpsEvent.now(
        event_type="daily_check",
        operator="tester",
        notes="All good",
    )

    store.append(ev)

    records = store.load("daily_check")
    assert len(records) == 1
    assert records[0]["operator"] == "tester"
