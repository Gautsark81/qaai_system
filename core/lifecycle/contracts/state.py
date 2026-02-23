from enum import Enum


class LifecycleState(str, Enum):
    """
    Canonical lifecycle states for a trading strategy.

    Design guarantees:
    - Closed set (no free-form strings)
    - Stable values (safe for persistence & replay)
    - Human-readable (dashboard & audit friendly)
    """

    # Newly generated strategy (not yet evaluated)
    GENERATED = "GENERATED"

    # Passed generation, under backtest / evaluation
    CANDIDATE = "CANDIDATE"

    # Approved for paper trading
    PAPER = "PAPER"

    # Actively trading with real capital
    LIVE = "LIVE"

    # Temporarily demoted due to SSR / health degradation
    DEGRADED = "DEGRADED"

    # Permanently retired — terminal state
    RETIRED = "RETIRED"

    # --------------------------------------------
    # Semantic helpers (pure, deterministic)
    # --------------------------------------------

    @property
    def is_terminal(self) -> bool:
        return self == LifecycleState.RETIRED

    @property
    def is_active(self) -> bool:
        return self in {
            LifecycleState.PAPER,
            LifecycleState.LIVE,
            LifecycleState.DEGRADED,
        }

    @property
    def is_trading(self) -> bool:
        return self == LifecycleState.LIVE
