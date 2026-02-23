from dataclasses import dataclass


@dataclass(frozen=True)
class ShadowDivergenceConfig:
    """
    Explicit enablement and thresholds for Shadow Divergence Engine.
    """
    enable_shadow_divergence: bool = False
    max_price_slippage_pct: float = 1.0
    max_capital_drift_pct: float = 1.0
