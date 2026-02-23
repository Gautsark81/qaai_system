from dataclasses import dataclass
from typing import Sequence, Optional
from datetime import datetime
import math

from core.regime.taxonomy import RegimeLabel


# ======================================================
# RAW REGIME SIGNALS (FEATURE LEVEL — EXISTING)
# ======================================================

@dataclass(frozen=True)
class RegimeSignals:
    """
    Canonical raw regime signals.

    All values are bounded and deterministic.
    """
    trend_strength: float      # [-1.0, +1.0]
    volatility_ratio: float    # >= 0.0
    correlation_stress: float  # [0.0, 1.0]


# =========================
# Signal Computation
# =========================

def compute_trend_strength(
    returns: Sequence[float],
    atr: float,
) -> float:
    """
    Trend strength = normalized slope of returns.

    Output is clipped to [-1, +1].
    """
    if not returns or atr <= 0:
        return 0.0

    slope = sum(returns) / len(returns)
    raw = slope / atr

    return max(-1.0, min(1.0, raw))


def compute_volatility_ratio(
    realized_vol: float,
    baseline_vol: float,
) -> float:
    """
    Volatility regime as ratio vs baseline.
    """
    if baseline_vol <= 0:
        return 1.0

    return max(0.0, realized_vol / baseline_vol)


def compute_correlation_stress(
    correlations: Sequence[float],
) -> float:
    """
    Correlation stress increases when dispersion collapses.

    Uses mean absolute correlation.
    """
    if not correlations:
        return 0.0

    avg_corr = sum(abs(c) for c in correlations) / len(correlations)
    return max(0.0, min(1.0, avg_corr))


# ======================================================
# CANONICAL REGIME SNAPSHOT (DASHBOARD / GOVERNANCE)
# ======================================================

@dataclass(frozen=True)
class RegimeSignal:
    """
    Canonical classified regime snapshot.

    This is what dashboards, explainability,
    and governance layers consume.
    """
    label: RegimeLabel
    confidence: float          # [0.0, 1.0]
    timestamp: datetime


# ======================================================
# INTERNAL LATEST SNAPSHOT (READ-ONLY OUTSIDE)
# ======================================================

_LATEST_REGIME_SIGNAL: Optional[RegimeSignal] = None


# ======================================================
# WRITE PATH (ENGINE ONLY)
# ======================================================

def record_regime_signal(signal: RegimeSignal) -> None:
    """
    Record the latest classified regime signal.

    Must only be called by the regime engine.
    """
    global _LATEST_REGIME_SIGNAL
    _LATEST_REGIME_SIGNAL = signal


# ======================================================
# READ PATH (DASHBOARD / OBSERVERS)
# ======================================================

def latest_regime_signal() -> Optional[RegimeSignal]:
    """
    Canonical, read-only accessor for the current regime.

    Used by:
    - Operator dashboard
    - Explainability
    - Governance views
    """
    return _LATEST_REGIME_SIGNAL
