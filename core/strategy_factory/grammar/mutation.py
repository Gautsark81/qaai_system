import random
from .constraints import MAX_MUTATION_DELTA
from .primitives import Primitive, PRIMITIVES
from .ast import ASTNode


def mutate_window(ast: ASTNode) -> ASTNode:
    if isinstance(ast.value, Primitive) and ast.value.param is not None:
        delta = random.randint(-MAX_MUTATION_DELTA, MAX_MUTATION_DELTA)
        return ASTNode(ast.value.mutate_window(delta))
    return ast


def mutate(ast: ASTNode) -> ASTNode:
    return mutate_window(ast)
