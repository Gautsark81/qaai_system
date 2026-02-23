"""
Symbol Context Contract
-----------------------
This defines the REQUIRED feature set that all strategy rules may consume.
No rule is allowed to access keys outside this contract.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SymbolContext:
    symbol: str

    # Price / volume structure
    price_above_vwap: bool
    vwap_slope_positive: bool
    volume_spike: bool

    # Trend structure
    trend_strength: float
    higher_high: bool
    higher_low: bool

    # Volatility
    atr_pct: float
    volatility_regime: str  # low / medium / high
