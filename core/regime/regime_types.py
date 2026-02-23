# core/regime/regime_types.py

from enum import Enum


class MarketRegime(str, Enum):
    TRENDING = "TRENDING"
    RANGING = "RANGING"
