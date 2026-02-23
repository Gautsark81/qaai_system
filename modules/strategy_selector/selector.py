from dataclasses import dataclass
from typing import Dict, List, Optional

from modules.strategy_health.state_machine import StrategyState


# ==========================================================
# CONFIG
# ==========================================================

@dataclass(frozen=True)
class SelectorConfig:
    allow_warning: bool = False
    allow_degraded: bool = False
    max_strategies_per_symbol: Optional[int] = None


# ==========================================================
# RESULT CONTRACT
# ==========================================================

@dataclass(frozen=True)
class SelectionResult:
    eligible: Dict[str, List[str]]       # symbol -> strategy_ids
    blocked: Dict[str, Dict[str, str]]   # symbol -> strategy_id -> reason


# ==========================================================
# STRATEGY SELECTOR
# ==========================================================

class StrategySelector:
    """
    Lifecycle-aware strategy selector.

    Guarantees:
    - Deterministic selection
    - Read-only enforcement
    - Full explainability
    """

    def __init__(self, *, config: SelectorConfig):
        self.config = config

    # ------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------

    def select(
        self,
        *,
        strategies_by_symbol: Dict[str, List[str]],
        states: Dict[str, StrategyState],
    ) -> SelectionResult:

        eligible: Dict[str, List[str]] = {}
        blocked: Dict[str, Dict[str, str]] = {}

        for symbol, strategy_ids in strategies_by_symbol.items():
            eligible[symbol] = []
            blocked[symbol] = {}

            for sid in strategy_ids:
                state = states.get(sid, StrategyState.RETIRED)

                allowed, reason = self._is_allowed(state)

                if allowed:
                    eligible[symbol].append(sid)
                else:
                    blocked[symbol][sid] = reason

            # Optional hard cap per symbol
            if self.config.max_strategies_per_symbol:
                eligible[symbol] = eligible[symbol][
                    : self.config.max_strategies_per_symbol
                ]

        return SelectionResult(
            eligible=eligible,
            blocked=blocked,
        )

    # ------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------

    def _is_allowed(self, state: StrategyState) -> (bool, str):
        if state == StrategyState.ACTIVE:
            return True, ""

        if state == StrategyState.WARNING:
            if self.config.allow_warning:
                return True, ""
            return False, "State=WARNING blocked by selector config"

        if state == StrategyState.DEGRADED:
            if self.config.allow_degraded:
                return True, ""
            return False, "State=DEGRADED blocked by selector config"

        return False, f"State={state.value} not eligible"
