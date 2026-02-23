from core.compliance.contracts.sebi import SEBITradeExport


def test_sebi_trade_export_contract_fields():
    export = SEBITradeExport(
        trade_id="T1",
        strategy_id="S1",
        symbol="NIFTY",
        side="BUY",
        quantity=50,
        price=22500.0,
        timestamp="2026-01-01T09:30:00Z",
    )

    record = export.to_record()

    assert "trade_id" in record
    assert "strategy_id" in record
    assert "symbol" in record
    assert "side" in record
    assert "quantity" in record
    assert "price" in record
    assert "timestamp" in record
