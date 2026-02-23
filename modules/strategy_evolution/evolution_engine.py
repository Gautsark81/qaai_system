from typing import List

from modules.strategy_genome.genome import StrategyGenome
from modules.strategy_genome.factory import StrategyGenomeFactory
from modules.strategy_evolution.mutations import MutationOperators, MutationSpec


class EvolutionEngine:
    """
    Offline evolution engine.

    Produces candidate genomes ONLY.
    """

    def __init__(
        self,
        *,
        genome_factory: StrategyGenomeFactory,
        mutation_ops: MutationOperators,
        max_children_per_parent: int = 3,
    ):
        self.factory = genome_factory
        self.mutation_ops = mutation_ops
        self.max_children = max_children_per_parent

    # ------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------

    def evolve(
        self,
        *,
        parents: List[StrategyGenome],
        seed: int,
    ) -> List[StrategyGenome]:
        """
        Evolves a population of parent genomes into candidate children.
        """
        candidates: List[StrategyGenome] = []

        for idx, parent in enumerate(parents):
            for m_idx, spec in enumerate(self.mutation_ops.specs):
                if m_idx >= self.max_children:
                    break

                new_params = self.mutation_ops.mutate_parameters(
                    parameters=parent.parameters,
                    spec=spec,
                    seed=seed + idx * 100 + m_idx,
                )

                child = self.factory.mutate(
                    parent=parent,
                    new_parameters=new_params,
                    mutation_reason=spec.reason,
                    seed=seed + idx * 100 + m_idx,
                )

                candidates.append(child)

        return candidates
