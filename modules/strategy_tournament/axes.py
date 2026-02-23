from enum import Enum

# =============================================================================
# MARKET CONTEXT AXES
# =============================================================================

class MarketStructure(str, Enum):
    TRENDING = "trending"
    BALANCED = "balanced"
    COMPRESSING = "compressing"
    EXPANDING = "expanding"
    EXHAUSTING = "exhausting"


class RegimeState(str, Enum):
    LOW_VOL = "low_vol"
    NORMAL_VOL = "normal_vol"
    HIGH_VOL = "high_vol"
    PANIC = "panic"


class RegimeTransition(str, Enum):
    NONE = "none"
    COMPRESSION_TO_EXPANSION = "compression_to_expansion"
    TREND_TO_BALANCE = "trend_to_balance"
    BALANCE_TO_TREND = "balance_to_trend"
    LOW_VOL_TO_HIGH_VOL = "low_vol_to_high_vol"


# =============================================================================
# MICROSTRUCTURE / EXECUTION AXES
# =============================================================================

class LiquidityModel(str, Enum):
    STOP_SWEEP = "stop_sweep"
    VWAP_REVERSION = "vwap_reversion"
    RANGE_EDGE = "range_edge"
    BREAKOUT_LIQUIDITY = "breakout_liquidity"
    ABSORPTION = "absorption"


class EfficiencyState(str, Enum):
    """
    Measures how efficiently price converts liquidity into movement.

    NOTE:
    - There is intentionally NO 'MEDIUM' state.
    - Efficiency is binary-biased by design:
        HIGH    → clean impulse
        LOW     → noisy / overlapping auction
        FAILED  → trapped / rejected move
    """
    HIGH = "high_efficiency"
    LOW = "low_efficiency"
    FAILED = "failed_efficiency"


# =============================================================================
# TIME / SESSION AXES
# =============================================================================

class SessionState(str, Enum):
    OPENING = "opening_discovery"
    RANGE = "range_formation"
    MID = "mid_session_balance"
    LATE = "late_session_positioning"
    EXPIRY = "expiry_distortion"


# =============================================================================
# STRATEGY INTENT AXES
# =============================================================================

class EntryType(str, Enum):
    BREAKOUT = "breakout"
    FADE = "fade"
    REVERSION = "reversion"
    CONTINUATION = "continuation"
    FAILED_BREAKOUT = "failed_breakout"


class RiskShape(str, Enum):
    FAST_STOP_FAST_TARGET = "fast_stop_fast_target"
    FAST_STOP_SLOW_TARGET = "fast_stop_slow_target"
    SLOW_STOP_FAST_TARGET = "slow_stop_fast_target"
    TRAILING_ONLY = "trailing_only"
    TIME_STOP = "time_stop"


class ExitIntent(str, Enum):
    TARGET_LIQUIDITY = "target_liquidity"
    VWAP_MEAN = "vwap_mean"
    VOLATILITY_COLLAPSE = "volatility_collapse"
    TIME_EXPIRY = "time_expiry"
    STRUCTURE_BREAK = "structure_break"


# =============================================================================
# PORTFOLIO ROLE AXIS (VERY IMPORTANT)
# =============================================================================

class PortfolioRole(str, Enum):
    """
    Defines WHY a strategy exists in the portfolio,
    not HOW it trades.
    """
    RETURN_GENERATOR = "return_generator"
    DRAWDOWN_HEDGE = "drawdown_hedge"
    VOLATILITY_DAMPENER = "volatility_dampener"
    REGIME_SENTINEL = "regime_sentinel"
    TAIL_RISK_CAPTURE = "tail_risk_capture"
