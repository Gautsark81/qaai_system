from core.strategy_factory.compiler import StrategyCompiler
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.primitives import Primitive


def test_basic_compile():
    ast = ASTNode(Primitive("Momentum", 20))
    compiler = StrategyCompiler()

    spec = compiler.compile(ast)

    assert spec.alpha_stream == "momentum"
    assert dict(spec.params)["window"] == 20
