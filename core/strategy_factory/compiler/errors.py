class CompilerError(Exception):
    """Base compiler error"""


class UnsupportedGrammarNode(CompilerError):
    pass


class CompilerConstraintViolation(CompilerError):
    pass
