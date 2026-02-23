from datetime import datetime


class TokenSessionGuard:
    def __init__(self, token_issued_at: datetime, ttl_hours: int = 24):
        self.token_issued_at = token_issued_at
        self.ttl_hours = ttl_hours

    def is_valid(self, now: datetime) -> bool:
        age = now - self.token_issued_at
        return age.total_seconds() < self.ttl_hours * 3600
