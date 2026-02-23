from enum import Enum


class MarketRegime(str, Enum):
    LOW_VOL = "low_vol"
    HIGH_VOL = "high_vol"
    TRENDING = "trending"
    RANGE_BOUND = "range_bound"
