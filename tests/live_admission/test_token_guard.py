from datetime import datetime, timedelta
from modules.live_admission.token_guard import TokenSessionGuard


def test_token_valid():
    issued = datetime.utcnow() - timedelta(hours=1)
    guard = TokenSessionGuard(issued)
    assert guard.is_valid(datetime.utcnow())


def test_token_expired():
    issued = datetime.utcnow() - timedelta(hours=25)
    guard = TokenSessionGuard(issued)
    assert not guard.is_valid(datetime.utcnow())
