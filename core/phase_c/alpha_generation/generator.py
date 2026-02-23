from typing import Iterable, List
from itertools import product

from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.registry import StrategyRegistry
from core.phase_c.alpha_generation.templates import StrategyTemplate


class AlphaGenerator:
    """
    Offline alpha idea generator.
    Produces GENERATED strategies only.
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def generate(
        self,
        *,
        template: StrategyTemplate,
        universe: Iterable[str],
        param_grid: dict,
    ) -> List[str]:
        dnas = []

        keys = list(param_grid.keys())
        values = list(param_grid.values())

        for combo in product(*values):
            params = dict(zip(keys, combo))

            spec = StrategySpec(
                name=f"{template.name}_{params}",
                alpha_stream=template.alpha_stream,
                timeframe=template.timeframe,
                universe=tuple(universe),
                params=params,
            )

            record = self.registry.register(spec)
            dnas.append(record.dna)

        return dnas
