# tests/test_position_manager_persistent.py
from qaai_system.execution.position_manager_persistent import PersistentPositionManager


def test_persistent_restore(tmp_path):
    path = tmp_path / "positions.jsonl"

    # First run: open, close position
    pm1 = PersistentPositionManager(store_path=path)
    pm1.on_fill("AAPL", "buy", 10, 100)
    pm1.on_fill("AAPL", "sell", 5, 110)
    snap1 = pm1.get_position("AAPL")
    assert snap1["qty"] == 5

    # Restart: reload persisted state
    pm2 = PersistentPositionManager(store_path=path)
    snap2 = pm2.get_position("AAPL")
    assert snap2["qty"] == 5
    assert snap2["realized_pnl"] > 0
