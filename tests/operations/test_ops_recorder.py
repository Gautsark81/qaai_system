from pathlib import Path

from core.operations.ops_recorder import OpsRecorder
from core.operations.ops_store import OpsEventStore


def test_ops_recorder_daily(tmp_path: Path):
    store = OpsEventStore(root_dir=tmp_path)
    rec = OpsRecorder(operator="ops_user", store=store)

    rec.record_daily_check("Checked dashboard")

    records = store.load("daily_check")
    assert len(records) == 1
    assert records[0]["notes"] == "Checked dashboard"
