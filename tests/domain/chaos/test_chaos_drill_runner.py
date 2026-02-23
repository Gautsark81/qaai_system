from datetime import datetime
from domain.chaos.chaos_event import ChaosEvent
from domain.chaos.chaos_scenario import ChaosScenario
from domain.chaos.chaos_drill_runner import ChaosDrillRunner


def test_chaos_drill_runner():
    scenario = ChaosScenario(
        "outage",
        [
            ChaosEvent("BROKER_DOWN", "broker", datetime.utcnow(), "lost"),
        ],
    )

    impacts = ChaosDrillRunner.run(scenario)
    assert impacts[0].should_halt_trading is True
