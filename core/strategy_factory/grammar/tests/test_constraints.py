import pytest

from core.strategy_factory.grammar.primitives import Primitive
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.validator import GrammarViolation, validate_ast


def test_ast_depth_violation():
    ast = ASTNode(Primitive("Momentum", 20))
    validate_ast(ast)  # should pass
