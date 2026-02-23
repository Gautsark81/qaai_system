from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.dna import compute_strategy_dna


class StrategyIntake:
    """
    ONLY entry point for new strategies.
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def submit(
        self,
        *,
        name: str,
        alpha_stream: str,
        timeframe: str,
        universe,
        params: dict,
    ) -> str:
        """
        Returns Strategy DNA.
        """
        spec = StrategySpec(
            name=name,
            alpha_stream=alpha_stream,
            timeframe=timeframe,
            universe=universe,
            params=params,
        )

        record = self.registry.register(spec)
        return record.dna
