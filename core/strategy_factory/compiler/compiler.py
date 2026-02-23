from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.primitives import Primitive
from core.strategy_factory.compiler.rules import (
    PRIMITIVE_TO_SIGNAL,
    DEFAULT_TIMEFRAME,
    DEFAULT_UNIVERSE,
    ALLOWED_PRIMITIVES,
)
from core.strategy_factory.compiler.errors import (
    UnsupportedGrammarNode,
    CompilerConstraintViolation,
)


class StrategyCompiler:
    """
    Deterministic compiler: Grammar AST → StrategySpec

    ❌ No execution
    ❌ No backtesting
    ❌ No signals
    """

    def compile(self, ast: ASTNode) -> StrategySpec:
        if not isinstance(ast.node, Primitive):
            raise UnsupportedGrammarNode("Root node must be a Primitive")

        primitive = ast.node

        if primitive.name not in ALLOWED_PRIMITIVES:
            raise CompilerConstraintViolation(
                f"Primitive not allowed: {primitive.name}"
            )

        signal_type = PRIMITIVE_TO_SIGNAL[primitive.name]

        params = {}
        if primitive.param is not None:
            params["window"] = primitive.param

        return StrategySpec(
            name=f"{primitive.name.lower()}_strategy",
            alpha_stream=signal_type,
            timeframe=DEFAULT_TIMEFRAME,
            universe=DEFAULT_UNIVERSE,
            params=params,
        )
