from enum import Enum
from typing import Dict


class KillScope(Enum):
    GLOBAL = "GLOBAL"
    SYMBOL = "SYMBOL"
    STRATEGY = "STRATEGY"


class KillSwitch:
    """
    Central, synchronous kill-switch.

    MUST be checked before:
    - order creation
    - order routing
    - execution confirmation
    """

    def __init__(self):
        self._global = False
        self._symbols: Dict[str, bool] = {}
        self._strategies: Dict[str, bool] = {}

    # -----------------------------
    # Activation
    # -----------------------------

    def activate_global(self):
        self._global = True

    def deactivate_global(self):
        self._global = False

    def block_symbol(self, symbol: str):
        self._symbols[symbol] = True

    def unblock_symbol(self, symbol: str):
        self._symbols.pop(symbol, None)

    def block_strategy(self, strategy_id: str):
        self._strategies[strategy_id] = True

    def unblock_strategy(self, strategy_id: str):
        self._strategies.pop(strategy_id, None)

    # -----------------------------
    # Enforcement
    # -----------------------------

    def is_blocked(self, *, symbol: str, strategy_id: str) -> bool:
        return (
            self._global
            or self._symbols.get(symbol, False)
            or self._strategies.get(strategy_id, False)
        )
