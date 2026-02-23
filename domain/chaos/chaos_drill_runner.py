from domain.chaos.chaos_scenario import ChaosScenario
from domain.chaos.chaos_evaluator import ChaosEvaluator
from domain.chaos.chaos_impact import ChaosImpact


class ChaosDrillRunner:
    """
    Runs chaos scenarios and returns impacts.
    """

    @staticmethod
    def run(scenario: ChaosScenario) -> list[ChaosImpact]:
        impacts = []
        for event in scenario.events:
            impacts.append(ChaosEvaluator.evaluate(event))
        return impacts
