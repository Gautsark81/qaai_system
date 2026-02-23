from core.live_trading.telemetry import TelemetryCollector


def test_telemetry_records_samples():
    t = TelemetryCollector()

    t.record(
        symbol="NIFTY",
        paper_price=100.0,
        live_price=101.0,
    )

    assert len(t.samples) == 1
    assert t.samples[0].symbol == "NIFTY"
