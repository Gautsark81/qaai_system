from core.strategy_factory.compiler import StrategyCompiler
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.primitives import Primitive


def test_compiler_deterministic():
    ast = ASTNode(Primitive("Momentum", 20))
    compiler = StrategyCompiler()

    s1 = compiler.compile(ast)
    s2 = compiler.compile(ast)

    assert s1 == s2
