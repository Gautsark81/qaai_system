from __future__ import annotations

from dataclasses import dataclass


class CapitalViolation(Exception):
    """Raised when a capital safety rule is violated."""
    pass


@dataclass(frozen=True)
class CapitalLimits:
    """
    Immutable capital safety configuration.

    All values are absolute limits.
    """

    max_total_exposure: float
    max_per_trade_exposure: float
    max_per_strategy_exposure: float


@dataclass(frozen=True)
class CapitalSnapshot:
    """
    Read-only view of current capital state.
    """

    total_exposure: float
    per_strategy_exposure: dict[str, float]


def assert_capital_allowed(
    *,
    trade_value: float,
    strategy_id: str,
    limits: CapitalLimits,
    snapshot: CapitalSnapshot,
) -> None:
    """
    Enforce capital safety rails.

    Raises CapitalViolation on any breach.
    """

    if trade_value > limits.max_per_trade_exposure:
        raise CapitalViolation(
            f"Trade exposure {trade_value} exceeds "
            f"per-trade limit {limits.max_per_trade_exposure}"
        )

    new_total = snapshot.total_exposure + trade_value
    if new_total > limits.max_total_exposure:
        raise CapitalViolation(
            f"Total exposure {new_total} exceeds "
            f"global limit {limits.max_total_exposure}"
        )

    strategy_current = snapshot.per_strategy_exposure.get(
        strategy_id, 0.0
    )
    new_strategy_total = strategy_current + trade_value

    if new_strategy_total > limits.max_per_strategy_exposure:
        raise CapitalViolation(
            f"Strategy '{strategy_id}' exposure {new_strategy_total} exceeds "
            f"limit {limits.max_per_strategy_exposure}"
        )
