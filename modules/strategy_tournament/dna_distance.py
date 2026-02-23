# modules/strategy_tournament/dna_distance.py

from modules.strategy_tournament.dna import StrategyDNA


def dna_distance(a: StrategyDNA, b: StrategyDNA) -> float:
    diffs = 0
    total = 0

    for field in a.__dataclass_fields__:
        total += 1
        if getattr(a, field) != getattr(b, field):
            diffs += 1

    return diffs / total if total > 0 else 0.0
