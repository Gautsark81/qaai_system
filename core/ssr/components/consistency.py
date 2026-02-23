from statistics import pstdev
from core.ssr.contracts.components import SSRComponentScore


class ConsistencyComponent:
    name = "consistency"

    def __init__(self, *, weight: float = 1.0):
        self.weight = weight

    def compute(self, *, inputs: dict) -> SSRComponentScore:
        returns = inputs.get("returns", [])

        if len(returns) < 2:
            return SSRComponentScore(
                name=self.name,
                score=0.0,
                weight=self.weight,
                metrics={},
            )

        volatility = pstdev(returns)
        score = max(0.0, 1.0 - volatility)

        return SSRComponentScore(
            name=self.name,
            score=round(min(score, 1.0), 4),
            weight=self.weight,
            metrics={"volatility": round(volatility, 6)},
        )
