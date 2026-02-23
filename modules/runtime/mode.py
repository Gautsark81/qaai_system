# modules/runtime/mode.py

from modules.runtime.context import get_runtime_flags


class TradingMode:
    """
    Centralized runtime mode guard.
    """

    @staticmethod
    def assert_can_trade() -> None:
        flags = get_runtime_flags()
        if flags.DRY_RUN:
            raise RuntimeError("DRY_RUN enabled: order submission blocked")
