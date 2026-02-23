from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime, timezone


# ------------------------------------------------------------------
# Market snapshot (raw inputs)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class MarketSnapshot:
    """
    Immutable raw market state for a symbol at a moment in time.
    Used by screening rules BEFORE scoring.
    """

    symbol: str
    timeframe: str

    close: float
    volume: float

    atr: Optional[float] = None
    volatility: Optional[float] = None

    features: Optional[Dict[str, float]] = None


# ------------------------------------------------------------------
# Derived screening snapshot (post-feature computation)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class ScreeningSnapshot:
    """
    Derived snapshot after feature computation.
    This is what gets scored & ranked.
    """

    symbol: str
    timeframe: str

    momentum: float
    liquidity: float

    score: Optional[float] = None
    rank: Optional[int] = None


# ------------------------------------------------------------------
# REQUIRED DOMAIN CONTRACT (DO NOT REMOVE)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class ScreeningDecision:
    """
    Canonical deterministic screening decision.
    This object is required across screening, strategies,
    watchlist, and legacy adapters.
    """

    symbol: str
    passed: bool
    reasons: List[str]
    score: float = 0.0
    generated_at: datetime = datetime.now(timezone.utc)


# ------------------------------------------------------------------
# Legacy compatibility (DO NOT REMOVE)
# ------------------------------------------------------------------

@dataclass
class ScreeningResult:
    """
    Legacy screening output.
    Must remain backward-compatible across screener, strategies,
    and watchlist layers.
    """

    symbol: str
    passed: bool
    reasons: list
    score: float
    liquidity: float = 0.0


@dataclass
class ScreenConfig:
    timeframe: str
    top_n: int
    min_liquidity: float = 0.0

    name: Optional[str] = None
    watchlist_name: Optional[str] = None
    prefer_feature_score: bool = True
