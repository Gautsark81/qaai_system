from typing import Dict

from modules.strategy_health.telemetry import StrategyTelemetry


class TelemetryAnalyzer:
    """
    High-level analytics over strategy telemetry.
    Read-only. Deterministic.
    """

    def __init__(self, telemetry: StrategyTelemetry):
        self.telemetry = telemetry

    def summary(self) -> Dict[str, object]:
        return {
            "strategy_id": self.telemetry.strategy_id,
            "total_steps": len(self.telemetry.health),
            "total_pauses": len(self.telemetry.pause_events()),
            "final_state": (
                self.telemetry.last_state().state
                if self.telemetry.last_state()
                else None
            ),
            "structural_decay_events": len(
                [d for d in self.telemetry.decay if d.level == "STRUCTURAL_DECAY"]
            ),
            "average_health": self._avg_health(),
        }

    def _avg_health(self) -> float:
        if not self.telemetry.health:
            return 0.0
        return round(
            sum(h.health_score for h in self.telemetry.health)
            / len(self.telemetry.health),
            4,
        )
