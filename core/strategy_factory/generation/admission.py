# core/strategy_factory/generation/admission.py
from core.strategy_factory.compiler.compiler import StrategyCompiler

class StrategyAdmissionController:
    def __init__(self, registry):
        self.registry = registry
        self.compiler = StrategyCompiler()

    def admit(self, ast):
        spec = self.compiler.compile(ast)
        return self.registry.register(spec)
