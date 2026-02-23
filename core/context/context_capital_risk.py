# core/context/context_capital_risk.py

from core.regime.regime_types import MarketRegime


class ReadOnlyDict(dict):
    """
    Dict that forbids mutation but supports deepcopy.
    """

    def __readonly__(self, *args, **kwargs):
        raise TypeError("This view is read-only")

    __setitem__ = __readonly__
    __delitem__ = __readonly__
    clear = __readonly__
    pop = __readonly__
    popitem = __readonly__
    setdefault = __readonly__
    update = __readonly__

    def __deepcopy__(self, memo):
        # Allow deepcopy to succeed without mutating this instance
        return ReadOnlyDict(self)


# ─────────────────────────────────────────────
# Capital View
# ─────────────────────────────────────────────

def build_capital_view(snapshot: dict) -> dict:
    """
    Deterministic, explanatory capital interpretation.
    NON-BINDING. READ-ONLY.
    """

    regime = snapshot.get("current_regime")

    if regime == MarketRegime.TRENDING:
        data = {
            "utilization_band": "NORMAL",
            "confidence": 0.8,
            "note": "Capital usage normal under trending regime.",
        }
    elif regime == MarketRegime.RANGING:
        data = {
            "utilization_band": "LOW",
            "confidence": 0.7,
            "note": "Reduced capital pressure under ranging regime.",
        }
    else:
        data = {
            "utilization_band": "UNKNOWN",
            "confidence": 0.5,
            "note": "Insufficient data for capital interpretation.",
        }

    return ReadOnlyDict(data)


# ─────────────────────────────────────────────
# Risk View
# ─────────────────────────────────────────────

def build_risk_view(snapshot: dict) -> dict:
    """
    Deterministic, explanatory risk interpretation.
    NON-BINDING. READ-ONLY.
    """

    regime = snapshot.get("current_regime")

    if regime == MarketRegime.TRENDING:
        data = {
            "risk_regime": "NORMAL",
            "confidence": 0.8,
            "note": "Risk conditions stable in trending regime.",
        }
    elif regime == MarketRegime.RANGING:
        data = {
            "risk_regime": "ELEVATED",
            "confidence": 0.7,
            "note": "Choppiness increases execution risk.",
        }
    else:
        data = {
            "risk_regime": "UNKNOWN",
            "confidence": 0.5,
            "note": "Risk regime unclear.",
        }

    return ReadOnlyDict(data)
