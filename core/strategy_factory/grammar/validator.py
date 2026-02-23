from .constraints import MAX_DEPTH, MAX_NODES
from .primitives import is_valid_primitive

class GrammarViolation(Exception):
    pass


def validate_ast(ast) -> None:
    if ast.depth() > MAX_DEPTH:
        raise GrammarViolation("AST exceeds maximum depth")

    if ast.node_count() > MAX_NODES:
        raise GrammarViolation("AST exceeds maximum node count")

    if not ast.children:
        if not is_valid_primitive(ast.value):
            raise ValueError(f"Invalid primitive: {ast.value}")

    for child in ast.children:
        validate_ast(child)


def validate(ast) -> None:
    validate_ast(ast)
