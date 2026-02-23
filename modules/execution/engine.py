# modules/execution/engine.py

from modules.execution.idempotency import ExecutionLedger
from modules.execution.plan_builder import build_execution_plan
from modules.order_manager.manager import OrderManager

class ExecutionEngine:
    def __init__(self, strategy_engine):
        self.strategy_engine = strategy_engine
        self.ledger = ExecutionLedger()

    def handle_execution_plan(self, plan):
        # idempotency at order layer
        self.order_manager.submit(plan)

    def on_intent(self, intent):
        plan = build_execution_plan(
            intent=intent,
            max_quantity=1,  # placeholder until G4 risk sizing
        )
        if plan is None:
            return
        self.handle_execution_plan(plan)

