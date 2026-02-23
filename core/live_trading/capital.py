from dataclasses import dataclass


@dataclass
class CapitalState:
    allocated: float
    used: float = 0.0
    pnl: float = 0.0


class CapitalLimitError(Exception):
    pass


class CapitalManager:
    """
    Enforces hard capital and loss limits per strategy.
    """

    def __init__(self, max_capital: float, max_daily_loss: float):
        self.max_capital = max_capital
        self.max_daily_loss = max_daily_loss
        self.state = CapitalState(allocated=max_capital)

    def assert_can_allocate(self, amount: float):
        if self.state.used + amount > self.max_capital:
            raise CapitalLimitError(
                "Capital limit exceeded"
            )

    def record_allocation(self, amount: float):
        self.assert_can_allocate(amount)
        self.state.used += amount

    def record_pnl(self, pnl: float):
        self.state.pnl += pnl

        if self.state.pnl < -self.max_daily_loss:
            raise CapitalLimitError(
                "Daily loss limit breached"
            )
