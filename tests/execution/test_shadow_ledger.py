from qaai_system.execution.shadow_ledger import ShadowLedger


def test_append_and_all():
    ledger = ShadowLedger()

    r1 = {"strategy_id": "s1", "symbol": "NIFTY"}
    r2 = {"strategy_id": "s2", "symbol": "BANKNIFTY"}

    ledger.append(r1)
    ledger.append(r2)

    out = ledger.all()

    assert len(out) == 2
    assert out[0]["strategy_id"] == "s1"
    assert out[1]["symbol"] == "BANKNIFTY"


def test_filter_by_strategy():
    ledger = ShadowLedger()

    ledger.append({"strategy_id": "s1", "symbol": "NIFTY"})
    ledger.append({"strategy_id": "s2", "symbol": "NIFTY"})
    ledger.append({"strategy_id": "s1", "symbol": "BANKNIFTY"})

    out = ledger.filter(strategy_id="s1")

    assert len(out) == 2
    assert all(r["strategy_id"] == "s1" for r in out)


def test_filter_by_symbol():
    ledger = ShadowLedger()

    ledger.append({"strategy_id": "s1", "symbol": "NIFTY"})
    ledger.append({"strategy_id": "s2", "symbol": "BANKNIFTY"})

    out = ledger.filter(symbol="BANKNIFTY")

    assert len(out) == 1
    assert out[0]["symbol"] == "BANKNIFTY"


def test_clear():
    ledger = ShadowLedger()

    ledger.append({"strategy_id": "s1"})
    ledger.clear()

    assert ledger.all() == []
