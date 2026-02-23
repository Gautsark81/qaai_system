from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.genome import Genome

def test_genome_exists_without_registry():
    g = Genome(ASTNode("price"))
    assert g.fingerprint()
