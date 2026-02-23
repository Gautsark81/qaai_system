from enum import Enum


class MarketRegime(str, Enum):
    """
    Canonical market regime taxonomy.

    These labels are advisory and descriptive only.
    """

    TRENDING = "TRENDING"
    MEAN_REVERTING = "MEAN_REVERTING"
    VOLATILE = "VOLATILE"
    RANGE_BOUND = "RANGE_BOUND"
    UNKNOWN = "UNKNOWN"
