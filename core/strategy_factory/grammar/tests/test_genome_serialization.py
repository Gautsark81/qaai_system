from core.strategy_factory.grammar.primitives import Primitive
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.genome import StrategyGenome


def test_genome_fingerprint_stable():
    ast = ASTNode(Primitive("Momentum", 20))
    genome = StrategyGenome("v1", ast, [])

    fp1 = genome.fingerprint()
    fp2 = genome.fingerprint()

    assert fp1 == fp2
