from typing import Dict, List

from modules.strategy_population.entry import PopulationEntry
from modules.strategy_population.fitness_snapshot import FitnessSnapshot
from modules.strategy_population.config import PopulationConfig
from modules.strategy_health.state_machine import StrategyState
from modules.strategy_genome.lineage_store import LineageStore


class PopulationManager:
    """
    Deterministic per-symbol population manager.

    Consumes:
    - FitnessSnapshot (C1 output)
    - StrategyState (C2)
    - Lineage (D1)

    Emits:
    - Curated population entries
    """

    def __init__(
        self,
        *,
        config: PopulationConfig,
        lineage_store: LineageStore,
    ):
        self.config = config
        self.lineage_store = lineage_store

    # ------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------

    def build_population(
        self,
        *,
        fitness: List[FitnessSnapshot],
        states: Dict[str, StrategyState],
        current_step: int,
    ) -> Dict[str, List[PopulationEntry]]:

        by_symbol: Dict[str, List[PopulationEntry]] = {}

        for f in fitness:
            state = states.get(f.strategy_id)
            if state not in {StrategyState.ACTIVE, StrategyState.WARNING}:
                continue

            if not self.config.allow_warning and state == StrategyState.WARNING:
                continue

            if f.fitness_score < self.config.min_fitness_threshold:
                continue

            lineage = self.lineage_store.get(f.strategy_id)
            age = current_step - f.evaluated_at_step

            if age > self.config.max_age_steps:
                continue

            entry = PopulationEntry(
                strategy_id=f.strategy_id,
                symbol=f.symbol,
                fitness_score=f.fitness_score,
                age_steps=age,
                state=state.value,
                generation=lineage.generation,
            )

            by_symbol.setdefault(f.symbol, []).append(entry)

        # Prune per symbol
        for symbol, entries in by_symbol.items():
            by_symbol[symbol] = self._prune(entries)

        return by_symbol

    # ------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------

    def _prune(self, entries: List[PopulationEntry]) -> List[PopulationEntry]:
        """
        Fitness-first, age-aware pruning.
        """
        # Sort by fitness desc, then age asc, then generation asc
        ordered = sorted(
            entries,
            key=lambda e: (-e.fitness_score, e.age_steps, e.generation),
        )

        # Enforce cap
        capped = ordered[: self.config.max_population_per_symbol]

        # Enforce diversity by generation (soft)
        seen_generations = set()
        diverse: List[PopulationEntry] = []

        for e in capped:
            if e.generation in seen_generations:
                continue
            seen_generations.add(e.generation)
            diverse.append(e)

        return diverse
