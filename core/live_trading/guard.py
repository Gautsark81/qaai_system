from core.strategy_factory.registry import StrategyRegistry
from core.live_trading.config import LiveTradingConfig
from core.strategy_factory.exceptions import ExecutionNotAllowed


class LiveExecutionGuard:
    """
    Final gate before LIVE trading.
    """

    def __init__(
        self,
        registry: StrategyRegistry,
        config: LiveTradingConfig,
    ):
        self.registry = registry
        self.config = config

    def assert_can_trade_live(self, dna: str):
        if not self.config.enabled:
            raise ExecutionNotAllowed("Live trading globally disabled")

        record = self.registry.get(dna)

        if record.state != "LIVE":
            raise ExecutionNotAllowed(
                f"Strategy {dna} not in LIVE state"
            )
