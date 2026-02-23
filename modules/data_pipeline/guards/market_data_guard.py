from datetime import datetime, timedelta


class MarketDataGuard:
    def __init__(self, cooldown_minutes=30):
        self._blocked = {}
        self.cooldown = timedelta(minutes=cooldown_minutes)

    def validate(self, symbol, bar, prev_bar):
        now = datetime.utcnow()

        if symbol in self._blocked:
            if now < self._blocked[symbol]:
                return False
            del self._blocked[symbol]

        if bar.close <= 0:
            self._blocked[symbol] = now + self.cooldown
            return False

        if prev_bar and bar.close == prev_bar.close and bar.volume == 0:
            self._blocked[symbol] = now + self.cooldown
            return False

        return True
