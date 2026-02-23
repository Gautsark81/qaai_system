from typing import List, Set

from modules.strategy_genome.genome import StrategyGenome


class DiversityFilter:
    """
    Prevents clone swarms by enforcing genome uniqueness.
    """

    def filter(self, genomes: List[StrategyGenome]) -> List[StrategyGenome]:
        seen: Set[str] = set()
        unique: List[StrategyGenome] = []

        for g in genomes:
            fp = g.fingerprint()
            if fp in seen:
                continue
            seen.add(fp)
            unique.append(g)

        return unique
