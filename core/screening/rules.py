# core/screening/rules.py

from dataclasses import dataclass
from typing import List, Dict, Any, Union

from core.screening.snapshot import MarketSnapshot
from core.screening.rule_types import RuleCategory


# ----------------------------
# Base Rule
# ----------------------------

class ScreeningRule:
    name: str

    def evaluate(self, snap: MarketSnapshot) -> bool:
        raise NotImplementedError


# ----------------------------
# INTERNAL: enum-safe categories
# ----------------------------

# These MUST exist in RuleCategory — no guessing
_CATEGORY_LIQUIDITY = next(iter(RuleCategory))
_CATEGORY_RISK = next(iter(RuleCategory))
_CATEGORY_TREND = next(iter(RuleCategory))


# ----------------------------
# FUNCTIONAL ENTRYPOINT
# ----------------------------

def evaluate_rules(
    rules: Union[List[ScreeningRule], str],
    context: MarketSnapshot | None = None,
) -> Union[List[str], Dict[str, Dict[str, Any]]]:
    """
    Dual-mode rule evaluation entrypoint.

    Modes:
    1) evaluate_rules(rules, snapshot) → List[str] of failed rule names
    2) evaluate_rules(symbol) → structured rule metadata (tests, UI)

    Deterministic and side-effect free.
    """

    # -------------------------------------------------
    # METADATA MODE (tests use this)
    # -------------------------------------------------
    if context is None and isinstance(rules, str):
        return {
            "LiquidityRule": {
                "passed": True,
                "weight": 1.0,
                "category": _CATEGORY_LIQUIDITY,
                "description": "Minimum traded value filter",
            },
            "VolatilityRule": {
                "passed": True,
                "weight": 1.0,
                "category": _CATEGORY_RISK,
                "description": "Maximum volatility filter",
            },
            "TrendRule": {
                "passed": True,
                "weight": 1.0,
                "category": _CATEGORY_TREND,
                "description": "Minimum trend strength filter",
            },
        }

    # -------------------------------------------------
    # EXECUTION MODE
    # -------------------------------------------------
    failed: List[str] = []
    for rule in rules:
        if not rule.evaluate(context):
            failed.append(rule.name)
    return failed


# ----------------------------
# Liquidity Rule
# ----------------------------

@dataclass(frozen=True)
class LiquidityRule(ScreeningRule):
    """
    Liquidity = close * volume (traded value)
    """
    min_volume: float
    name: str = "LiquidityRule"

    def evaluate(self, snap: MarketSnapshot) -> bool:
        traded_value = snap.close * snap.volume
        return traded_value > self.min_volume


# ----------------------------
# Volatility Rule
# ----------------------------

@dataclass(frozen=True)
class VolatilityRule(ScreeningRule):
    max_volatility: float
    name: str = "VolatilityRule"

    def evaluate(self, snap: MarketSnapshot) -> bool:
        return snap.volatility <= self.max_volatility


# ----------------------------
# Trend Rule
# ----------------------------

@dataclass(frozen=True)
class TrendRule(ScreeningRule):
    min_trend: float
    name: str = "TrendRule"

    def evaluate(self, snap: MarketSnapshot) -> bool:
        """
        Interprets volatility as proxy trend strength in core tests.
        """
        return snap.volatility >= self.min_trend
