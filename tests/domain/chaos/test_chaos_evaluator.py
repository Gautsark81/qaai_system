from datetime import datetime
from domain.chaos.chaos_event import ChaosEvent
from domain.chaos.chaos_evaluator import ChaosEvaluator


def test_critical_event_halts_trading():
    e = ChaosEvent("FEED_GAP", "data", datetime.utcnow(), "missing ticks")
    impact = ChaosEvaluator.evaluate(e)
    assert impact.should_halt_trading is True
