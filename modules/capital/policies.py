from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalPolicy:
    """
    Capital scaling policy (conservative by default).

    This policy defines the SAFE OPERATING ENVELOPE
    for all capital decisions.
    """

    # Drawdown control
    max_drawdown_pct: float = 0.20
    min_scale: float = 0.20
    max_scale: float = 1.00

    # Volatility control (soft throttle)
    volatility_cap: float = 0.04          # 4% rolling vol
    volatility_min_scale: float = 0.60

    # Liquidity control
    min_cash_ratio: float = 0.10
    cash_min_scale: float = 0.30

    # Absolute safety
    hard_cap_notional: float | None = None

    def clamp_scale(self, s: float) -> float:
        """
        Absolute safety clamp.
        """
        if s < self.min_scale:
            return self.min_scale
        if s > self.max_scale:
            return self.max_scale
        return s
