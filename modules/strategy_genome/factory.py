from typing import Dict, Any, Optional

from modules.strategy_genome.genome import StrategyGenome
from modules.strategy_genome.lineage import LineageRecord
from modules.strategy_genome.lineage_store import LineageStore


# ==========================================================
# GENOME FACTORY
# ==========================================================

class StrategyGenomeFactory:
    """
    Only approved way to create or mutate genomes.
    """

    def __init__(self, lineage_store: LineageStore):
        self.lineage_store = lineage_store

    # ------------------------------------------------------
    # ROOT GENOME
    # ------------------------------------------------------

    def create_root(
        self,
        *,
        strategy_type: str,
        symbol_universe: str,
        timeframe: str,
        parameters: Dict[str, Any],
        features: Dict[str, Any],
        seed: int,
        created_by: str = "manual",
    ) -> StrategyGenome:

        genome = StrategyGenome(
            strategy_type=strategy_type,
            symbol_universe=symbol_universe,
            timeframe=timeframe,
            parameters=parameters,
            features=features,
            seed=seed,
        )

        strategy_id = genome.fingerprint()

        self.lineage_store.add(
            LineageRecord(
                strategy_id=strategy_id,
                parent_id=None,
                generation=0,
                mutation_reason=None,
                created_by=created_by,
            )
        )

        return genome

    # ------------------------------------------------------
    # MUTATION
    # ------------------------------------------------------

    def mutate(
        self,
        *,
        parent: StrategyGenome,
        new_parameters: Optional[Dict[str, Any]] = None,
        new_features: Optional[Dict[str, Any]] = None,
        mutation_reason: str,
        seed: int,
        created_by: str = "evolution_engine",
    ) -> StrategyGenome:

        genome = StrategyGenome(
            strategy_type=parent.strategy_type,
            symbol_universe=parent.symbol_universe,
            timeframe=parent.timeframe,
            parameters=new_parameters or parent.parameters,
            features=new_features or parent.features,
            parent_id=parent.fingerprint(),
            generation=parent.generation + 1,
            mutation_reason=mutation_reason,
            seed=seed,
        )

        strategy_id = genome.fingerprint()

        self.lineage_store.add(
            LineageRecord(
                strategy_id=strategy_id,
                parent_id=parent.fingerprint(),
                generation=genome.generation,
                mutation_reason=mutation_reason,
                created_by=created_by,
            )
        )

        return genome
