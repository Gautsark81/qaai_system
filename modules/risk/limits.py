# modules/risk/limits.py

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLimits:
    max_gross_exposure_pct: float
    max_atr_loss_pct: float
    max_volatility: float
    max_symbol_pct: float
