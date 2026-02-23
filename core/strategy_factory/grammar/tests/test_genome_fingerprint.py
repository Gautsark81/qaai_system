from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.genome import Genome

def test_deterministic_hash():
    g1 = Genome(ASTNode("price"))
    g2 = Genome(ASTNode("price"))
    assert g1.fingerprint() == g2.fingerprint()
