def test_no_telemetry_on_noop(telemetry_sink):
    # simulate no decision taken
    assert telemetry_sink.events == []
