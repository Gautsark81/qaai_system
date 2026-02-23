# core/strategy_factory/generation/mutation_policy.py
import random
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.primitives import Primitive

def mutate_ast(ast: ASTNode, seed: int) -> ASTNode:
    random.seed(seed)

    if not isinstance(ast.node, Primitive):
        return ast

    delta = random.choice([-5, 5, -10, 10])
    new_param = max(1, ast.node.param + delta)

    mutated = Primitive(ast.node.name, new_param)
    return ASTNode(mutated, ast.children)
