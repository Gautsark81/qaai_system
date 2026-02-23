from dataclasses import dataclass

from core.capital.result import CapitalAllocationResult


@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    price: float
    quantity: int


@dataclass(frozen=True)
class SlippageModel:
    """
    Deterministic slippage model.
    Example: 0.01 = 1% worst-case slippage
    """
    max_slippage_pct: float

    def worst_case_multiplier(self) -> float:
        return 1.0 + self.max_slippage_pct


@dataclass(frozen=True)
class OrderGateResult:
    allowed: bool
    reason: str


class SlippageGate:
    """
    Hard capital enforcement against worst-case slippage.
    """

    def evaluate(
        self,
        *,
        allocation: CapitalAllocationResult,
        order: OrderIntent,
        slippage: SlippageModel,
    ) -> OrderGateResult:
        worst_case_cost = (
            order.price
            * order.quantity
            * slippage.worst_case_multiplier()
        )

        if worst_case_cost > allocation.allocated_capital:
            return OrderGateResult(
                allowed=False,
                reason="ORDER_BLOCKED_SLIPPAGE_CAPITAL_BREACH",
            )

        return OrderGateResult(
            allowed=True,
            reason="ORDER_PASSED_SLIPPAGE_CHECK",
        )
