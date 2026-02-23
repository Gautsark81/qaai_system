from __future__ import annotations

import random
from typing import Dict, Any


# ============================================================
# Indicator Catalog
# ============================================================

INDICATORS = {
    "RSI": {"params": {"period": (7, 21), "threshold": (40, 70)}},
    "SUPERTREND": {"params": {"period": (7, 14), "multiplier": (2.0, 4.0)}},
    "VWAP": {"params": {"deviation": (0.5, 2.5)}},
    "BREAKOUT": {"params": {"lookback": (10, 50)}},
    "SUPPORT_RESISTANCE": {
        "params": {"lookback": (20, 100), "buffer_pct": (0.2, 1.5)}
    },
}

NEWS_HOOK = {
    "mode": ["block", "size_reduce"],
    "severity_threshold": [1, 2, 3],
}


# ============================================================
# Helpers
# ============================================================

def _rand(lo, hi):
    return round(random.uniform(lo, hi), 4)


def _mutate(v, lo, hi, pct=0.25):
    delta = (hi - lo) * pct
    return max(lo, min(hi, _rand(v - delta, v + delta)))


# ============================================================
# SCHEMA NORMALIZATION (CRITICAL FIX)
# ============================================================

def normalize_entry_schema(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts legacy entry schema into canonical form.

    Legacy:
        {"indicator": "RSI", "threshold": 55}

    Canonical:
        {
            "indicator": {
                "type": "RSI",
                "params": {...}
            }
        }
    """
    if isinstance(entry.get("indicator"), dict):
        return dict(entry)

    # Legacy schema
    indicator = entry.get("indicator")
    if indicator not in INDICATORS:
        return dict(entry)

    params = {}
    for k, bounds in INDICATORS[indicator]["params"].items():
        if k in entry:
            params[k] = entry[k]
        elif isinstance(bounds, tuple):
            params[k] = _rand(*bounds)

    return {
        "indicator": {
            "type": indicator,
            "params": params,
        }
    }


# ============================================================
# Indicator Generation
# ============================================================

def generate_indicator(name: str) -> Dict[str, Any]:
    spec = INDICATORS[name]
    return {
        "type": name,
        "params": {
            k: (_rand(*v) if isinstance(v, tuple) else random.choice(v))
            for k, v in spec["params"].items()
        },
    }


def random_indicator(exclude: str | None = None) -> Dict[str, Any]:
    names = list(INDICATORS.keys())
    if exclude in names:
        names.remove(exclude)
    return generate_indicator(random.choice(names))


# ============================================================
# ENTRY MUTATION (SAFE & EVOLVABLE)
# ============================================================

def mutate_entry_logic(entry: Dict[str, Any]) -> Dict[str, Any]:
    entry = normalize_entry_schema(entry)
    mutated = dict(entry)

    indicator = mutated.get("indicator")
    if not indicator:
        return mutated

    # Indicator switch
    if random.random() < 0.5:
        mutated["indicator"] = random_indicator(exclude=indicator["type"])

    # Param drift
    for p, v in mutated["indicator"]["params"].items():
        bounds = INDICATORS[mutated["indicator"]["type"]]["params"].get(p)
        if isinstance(bounds, tuple):
            mutated["indicator"]["params"][p] = _mutate(v, bounds[0], bounds[1])

    # Optional news gate
    if random.random() < 0.3:
        mutated["news_filter"] = {
            "type": "NEWS_IMPACT",
            "params": {
                "mode": random.choice(NEWS_HOOK["mode"]),
                "severity_threshold": random.choice(NEWS_HOOK["severity_threshold"]),
            },
        }

    return mutated
