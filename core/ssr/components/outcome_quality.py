from statistics import mean
from core.ssr.contracts.components import SSRComponentScore


class OutcomeQualityComponent:
    name = "outcome_quality"

    def __init__(self, *, weight: float = 1.0):
        self.weight = weight

    def compute(self, *, inputs: dict) -> SSRComponentScore:
        returns = inputs.get("returns", [])
        expectancy = float(inputs.get("expectancy", 0.0))
        win_rate = float(inputs.get("win_rate", 0.0))

        if not returns:
            score = 0.0
        else:
            avg_ret = mean(returns)
            score = max(
                0.0,
                min(
                    1.0,
                    0.5 * (avg_ret > 0) + 0.5 * win_rate,
                ),
            )

        return SSRComponentScore(
            name=self.name,
            score=round(score, 4),
            weight=self.weight,
            metrics={
                "expectancy": round(expectancy, 6),
                "win_rate": round(win_rate, 4),
            },
        )
