from dataclasses import dataclass
from .enums import StabilityLevel


@dataclass(frozen=True)
class StabilityFingerprint:
    parameter_sensitivity: StabilityLevel
    regime_dependence: StabilityLevel
    sample_efficiency: StabilityLevel
    backtest_variance: StabilityLevel
