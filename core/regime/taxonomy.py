from enum import Enum
from dataclasses import dataclass


# ======================================================
# Legacy / Signal-Level Regime Labels (KEEP)
# ======================================================

class RegimeLabel(str, Enum):
    NORMAL = "NORMAL"
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"
    STRESSED = "STRESSED"
    UNKNOWN = "UNKNOWN"


# ======================================================
# Trend Regime (Directional – USED BY CLASSIFIER TESTS)
# ======================================================

class TrendRegime(Enum):
    TRENDING_UP = "TREND"
    RANGE = "RANGE"


# ======================================================
# Volatility Regime (STABLE VALUES – ASSERTED BY TESTS)
# ======================================================

class VolatilityRegime(Enum):
    LOW = "LOW_VOL"
    HIGH = "HIGH_VOL"


# ======================================================
# Market Regime (Primary – REQUIRED BY ALL REGIME TESTS)
# ======================================================

class MarketRegime(Enum):
    TREND_LOW_VOL = "TREND_LOW_VOL"
    TREND_HIGH_VOL = "TREND_HIGH_VOL"
    RANGE_LOW_VOL = "RANGE_LOW_VOL"
    RANGE_HIGH_VOL = "RANGE_HIGH_VOL"
    CHAOTIC = "CHAOTIC"


# ======================================================
# Strategy Health (LEGACY ENUM – KEEP FOR NOW)
# NOTE: This will be replaced by a class in health.py
# ======================================================

class StrategyHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    RETIRED = "RETIRED"


# ======================================================
# Composite Snapshot (Observational Only)
# ======================================================

@dataclass(frozen=True)
class RegimeSnapshot:
    market: MarketRegime
    volatility: VolatilityRegime
    trend: TrendRegime
    confidence: float
