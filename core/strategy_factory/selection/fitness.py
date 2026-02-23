from dataclasses import dataclass
from core.strategy_factory.grammar.ast import ASTNode


def _count_nodes(ast: ASTNode) -> int:
    return 1 + sum(_count_nodes(c) for c in ast.children)


@dataclass(frozen=True)
class FitnessScore:
    stability: float
    simplicity: float
    novelty: float

    @property
    def total(self) -> float:
        return round(
            0.45 * self.stability +
            0.35 * self.simplicity +
            0.20 * self.novelty,
            6,
        )


def evaluate_fitness(ast: ASTNode) -> FitnessScore:
    depth = ast.depth()
    nodes = _count_nodes(ast)

    stability = max(0.0, 1.0 - depth * 0.15)
    simplicity = max(0.0, 1.0 - nodes * 0.10)
    novelty = 0.5  # placeholder — Phase-11

    return FitnessScore(
        stability=stability,
        simplicity=simplicity,
        novelty=novelty,
    )
