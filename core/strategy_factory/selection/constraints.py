from core.strategy_factory.grammar.ast import ASTNode

# Selection-stage limits (INTENTIONALLY STRICT)
MAX_DEPTH = 4
MAX_NODES = 5   # 👈 THIS is the key fix


def _count_nodes(ast: ASTNode) -> int:
    return 1 + sum(_count_nodes(c) for c in ast.children)


def assert_selection_constraints(ast: ASTNode) -> None:
    if ast.depth() > MAX_DEPTH:
        raise ValueError("AST depth exceeds selection limit")

    if _count_nodes(ast) > MAX_NODES:
        raise ValueError("AST node count exceeds selection limit")
