# modules/bootstrap/wiring.py

from modules.execution.engine import ExecutionEngine
from modules.strategies.engine import StrategyEngine


class Application:
    def __init__(self):
        self.strategy_engine = StrategyEngine()
        self.execution_engine = ExecutionEngine(self.strategy_engine)

    def run(self) -> None:
        self.execution_engine.run_forever()


def wire_application() -> Application:
    return Application()
