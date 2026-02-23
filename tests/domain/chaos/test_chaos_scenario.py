from datetime import datetime
from domain.chaos.chaos_event import ChaosEvent
from domain.chaos.chaos_scenario import ChaosScenario


def test_chaos_scenario():
    s = ChaosScenario(
        name="broker_outage",
        events=[
            ChaosEvent("BROKER_DOWN", "broker", datetime.utcnow(), "lost"),
        ],
    )
    assert s.name == "broker_outage"
