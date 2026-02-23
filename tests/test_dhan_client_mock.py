# tests/test_dhan_client_mock.py
from data.ingestion.dhan_client import DhanClientMock


def test_dhan_mock_tick():
    c = DhanClientMock()
    assert c.connect() is True
    c.set_last_price("SYM", 123.45)
    t = c.get_last_tick("SYM")
    assert t["symbol"] == "SYM" and abs(t["price"] - 123.45) < 1e-6
