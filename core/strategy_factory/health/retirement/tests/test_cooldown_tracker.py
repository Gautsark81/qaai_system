from datetime import datetime, timedelta
from core.strategy_factory.health.retirement.cooldown_tracker import CooldownTracker

def test_cooldown_expiry():
    tracker = CooldownTracker(datetime.utcnow(), 1)
    assert tracker.is_expired(datetime.utcnow() + timedelta(days=2))
