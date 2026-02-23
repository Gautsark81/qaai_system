from qaai_system.execution.position_store import JSONLPositionStore


def test_position_store_persistence(tmp_path):
    store_path = tmp_path / "positions.jsonl"

    store = JSONLPositionStore(str(store_path))
    store.update_position("AAPL", 10, 150.0, 50.0)
    store.update_position("TSLA", -5, 700.0, -100.0)

    # reload
    store2 = JSONLPositionStore(str(store_path))
    pos = store2.all_positions()

    symbols = {p["symbol"] for p in pos}
    assert "AAPL" in symbols
    assert "TSLA" in symbols
    assert store2.positions["AAPL"]["qty"] == 10
    assert store2.positions["TSLA"]["realized_pnl"] == -100.0
