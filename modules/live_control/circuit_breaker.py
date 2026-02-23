class CircuitBreaker:
    """
    Trips system-level kill-switch on abnormal behavior.
    """

    def __init__(
        self,
        *,
        max_daily_loss: float,
        max_consecutive_errors: int,
    ):
        self.max_daily_loss = max_daily_loss
        self.max_consecutive_errors = max_consecutive_errors

        self._loss = 0.0
        self._errors = 0

    def record_pnl(self, pnl: float):
        if pnl < 0:
            self._loss += abs(pnl)

    def record_error(self):
        self._errors += 1

    def should_trip(self) -> bool:
        return (
            self._loss >= self.max_daily_loss
            or self._errors >= self.max_consecutive_errors
        )

    def reset(self):
        self._loss = 0.0
        self._errors = 0
