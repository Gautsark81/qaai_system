import random
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.primitives import Primitive
from core.strategy_factory.compiler.compiler import ALLOWED_PRIMITIVES

# Deterministic, governance-approved parameter space
WINDOWS = [5, 10, 20, 50]


def generate_ast(seed: int) -> ASTNode:
    """
    Generate a deterministic, compiler-safe AST.

    Guarantees:
    - Deterministic for a given seed
    - Root node is always a Primitive
    - Primitive is compiler-approved
    - Safe for direct admission → compilation → registry
    """
    random.seed(seed)

    # IMPORTANT:
    # Generator must only emit compiler-allowed primitives
    name = random.choice(tuple(ALLOWED_PRIMITIVES))
    window = random.choice(WINDOWS)

    primitive = Primitive(name, window)
    return ASTNode(primitive)
