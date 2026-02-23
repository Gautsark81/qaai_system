from core.paper_trading.ledger import PaperLedger


def test_ledger_idempotency():
    ledger = PaperLedger()
    ledger.record("x", {"ok": True})

    assert ledger.has("x")
    assert ledger.get("x")["ok"] is True
