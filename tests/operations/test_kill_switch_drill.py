from pathlib import Path

from core.operations.ops_recorder import OpsRecorder
from core.operations.ops_store import OpsEventStore


def test_kill_switch_drill_recorded(tmp_path: Path):
    store = OpsEventStore(root_dir=tmp_path)
    rec = OpsRecorder(operator="ops_user", store=store)

    rec.record_kill_switch_drill("Kill switch armed and disarmed successfully")

    records = store.load("kill_switch_drill")
    assert len(records) == 1
    assert "armed" in records[0]["notes"]
