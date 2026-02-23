from modules.live_control.circuit_breaker import CircuitBreaker


def test_loss_trips_breaker():
    cb = CircuitBreaker(max_daily_loss=1000, max_consecutive_errors=10)

    cb.record_pnl(-400)
    cb.record_pnl(-700)

    assert cb.should_trip()


def test_error_trips_breaker():
    cb = CircuitBreaker(max_daily_loss=1000, max_consecutive_errors=3)

    cb.record_error()
    cb.record_error()
    cb.record_error()

    assert cb.should_trip()


def test_reset():
    cb = CircuitBreaker(max_daily_loss=100, max_consecutive_errors=1)
    cb.record_error()
    assert cb.should_trip()

    cb.reset()
    assert not cb.should_trip()
