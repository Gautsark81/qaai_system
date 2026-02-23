from enum import Enum


class StrategyFamily(str, Enum):
    TREND = "trend"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    STAT_ARB = "stat_arb"
    VOLATILITY = "volatility"
    HYBRID = "hybrid"


class GenerationSource(str, Enum):
    HUMAN = "human"
    STRATEGY_FACTORY = "strategy_factory"
    MUTATION_ENGINE = "mutation_engine"


class LifecycleStage(str, Enum):
    GENERATED = "generated"
    BACKTESTED = "backtested"
    PAPER = "paper"
    LIVE = "live"
    RETIRED = "retired"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StabilityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    STABLE = "stable"
    MODERATE = "moderate"
    FRAGILE = "fragile"
