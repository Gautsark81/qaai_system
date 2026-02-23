import pytest
from core.strategy_factory.compiler import StrategyCompiler
from core.strategy_factory.compiler.errors import CompilerConstraintViolation
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.primitives import Primitive


def test_reject_unknown_primitive():
    ast = ASTNode(Primitive("UnknownAlpha", 10))
    compiler = StrategyCompiler()

    with pytest.raises(CompilerConstraintViolation):
        compiler.compile(ast)
