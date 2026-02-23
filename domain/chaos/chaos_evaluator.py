from domain.chaos.chaos_detector import ChaosDetector
from domain.chaos.chaos_event import ChaosEvent
from domain.chaos.chaos_impact import ChaosImpact


class ChaosEvaluator:
    """
    Maps chaos events to system impact.
    """

    @staticmethod
    def evaluate(event: ChaosEvent) -> ChaosImpact:
        if ChaosDetector.is_critical(event):
            return ChaosImpact(
                should_halt_trading=True,
                severity="CRITICAL",
            )

        return ChaosImpact(
            should_halt_trading=False,
            severity="LOW",
        )
