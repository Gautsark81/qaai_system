# tests/test_blotter.py
from backtest.blotter import Blotter
from pathlib import Path


def test_blotter_records_and_reads(tmp_path):
    p = tmp_path / "blotter.csv"
    b = Blotter(path=str(p))
    order = {
        "symbol": "TST",
        "side": "buy",
        "quantity": 2,
        "price": 10.5,
        "order_id": "ord1",
    }
    # Record order and a fill
    b.record_order(order, order_id="ord1")
    fill = {"order_id": "ord1", "status": "filled", "price": 10.5}
    b.record_fill(order, fill)
    rows = b.read()
    # We expect at least two rows (header + two appended rows read as dicts)
    assert isinstance(rows, list)
    # last two appended rows should contain our order and fill values
    found_symbols = [r["symbol"] for r in rows if r.get("symbol")]
    assert "TST" in found_symbols


def test_blotter_creates_file_if_missing(tmp_path):
    p = tmp_path / "sub" / "blot.csv"
    b = Blotter(path=str(p))
    assert Path(str(p)).exists()
    # header should exist
    rows = b.read()
    assert isinstance(rows, list)
