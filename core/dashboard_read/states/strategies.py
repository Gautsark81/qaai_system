@dataclass(frozen=True)
class StrategyState:
    active: int
    at_risk: int
    retiring: int
    retired: int
