from typing import Dict

# Mapping from grammar primitive → StrategySpec fields
PRIMITIVE_TO_SIGNAL: Dict[str, str] = {
    "Momentum": "momentum",
    "MeanReversion": "mean_reversion",
}

DEFAULT_TIMEFRAME = "5m"
DEFAULT_UNIVERSE = ["NIFTY"]

ALLOWED_PRIMITIVES = set(PRIMITIVE_TO_SIGNAL.keys())
