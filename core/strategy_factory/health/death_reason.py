from enum import Enum


class DeathReason(Enum):
    """
    Canonical reasons for strategy death.

    Semantics are LOCKED.
    These values are persisted, audited, and used for learning.
    """

    MAX_DRAWDOWN = "max_drawdown"
    SSR_FAILURE = "ssr_failure"
    CONSECUTIVE_LOSSES = "consecutive_losses"
    VOLATILITY_REGIME = "volatility_regime"
    MARKET_STRUCTURE = "market_structure"
    OPERATOR_KILL = "operator_kill"
    SYSTEM_GUARDRAIL = "system_guardrail"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_str(cls, value: str) -> "DeathReason":
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f"Unknown DeathReason: {value}") from exc
