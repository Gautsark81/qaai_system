from dataclasses import dataclass


@dataclass(frozen=True)
class CanaryEnvelope:
    min_trade_capital: float   # ₹
    max_trade_capital: float   # ₹

    def clamp(self, requested: float) -> float | None:
        if requested < self.min_trade_capital:
            return None
        if requested > self.max_trade_capital:
            return None
        return requested
