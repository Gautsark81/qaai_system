from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceShapeFingerprint:
    win_rate_bucket: str
    payoff_ratio_bucket: str
    drawdown_profile: str
    equity_curve_shape: str
