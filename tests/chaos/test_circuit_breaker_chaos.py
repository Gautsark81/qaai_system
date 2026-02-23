from modules.live_control.circuit_breaker import CircuitBreaker

def test_extreme_loss_trips_breaker():
    cb = CircuitBreaker(max_daily_loss=1000, max_consecutive_errors=100)
    for _ in range(20):
        cb.record_pnl(-100)
    assert cb.should_trip()
