from dataclasses import dataclass

from core.live_ops.enums import TradingMode


@dataclass(frozen=True, slots=True)
class SystemRunContext:
    """
    System run metadata.

    Created at bootstrap.
    Immutable for entire run.
    """
    run_id: str
    trading_mode: TradingMode
    capital: float
    max_positions: int
