# execution/order_manager_with_risk.py
from __future__ import annotations

from typing import Any, Dict, Callable
from qaai_system.execution.risk_manager import RiskLimitViolation

class OrderManagerWithRisk:
    """
    Risk-wrapped OrderManager.

    Responsibilities:
    - Run RiskManager.pre_submit() BEFORE any order submission
    - Treat RiskManager as exception-based (no boolean returns)
    - Forward orders to the inner OrderManager ONLY if risk passes
    - Never swallow RiskLimitViolation
    """

    def __init__(
        self,
        inner,
        risk_manager,
        portfolio_state_getter: Callable[[], Dict[str, Any]],
    ):
        self.inner = inner
        self.risk_manager = risk_manager
        self.portfolio_state_getter = portfolio_state_getter

    def submit_order(self, order: Dict[str, Any]) -> Any:
        state = self.portfolio_state_getter()

        # ABSOLUTE RISK GATE (exception-based)
        self.risk_manager.pre_submit(order, state)

        return self.inner.submit_order(order)

    # Optional passthroughs for interface parity
    def cancel_order(self, *args, **kwargs):
        if hasattr(self.inner, "cancel_order"):
            return self.inner.cancel_order(*args, **kwargs)
        raise NotImplementedError("Inner OrderManager does not support cancel_order")

    def get_order_status(self, *args, **kwargs):
        if hasattr(self.inner, "get_order_status"):
            return self.inner.get_order_status(*args, **kwargs)
        raise NotImplementedError("Inner OrderManager does not support get_order_status")


