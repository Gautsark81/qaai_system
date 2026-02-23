from core.ssr.contracts.components import SSRComponentScore
from core.strategy_health.contracts.enums import HealthStatus


class HealthStabilityComponent:
    name = "health_stability"

    def __init__(self, *, weight: float = 1.0):
        self.weight = weight

    def compute(self, *, inputs: dict) -> SSRComponentScore:
        snaps = inputs.get("health_snapshots", [])

        if not snaps:
            return SSRComponentScore(
                name=self.name,
                score=0.0,
                weight=self.weight,
                metrics={},
            )

        weights = {
            HealthStatus.HEALTHY: 1.0,
            HealthStatus.DEGRADED: 0.5,
            HealthStatus.CRITICAL: 0.0,
            HealthStatus.DISABLED: 0.0,
        }

        total = sum(weights.get(s.status, 0.0) for s in snaps)
        score = total / len(snaps)

        return SSRComponentScore(
            name=self.name,
            score=round(score, 4),
            weight=self.weight,
            metrics={
                "healthy_ratio": round(
                    sum(1 for s in snaps if s.status == HealthStatus.HEALTHY)
                    / len(snaps),
                    4,
                )
            },
        )
