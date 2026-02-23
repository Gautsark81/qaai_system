from core.resilience.capital_freeze.choreographer import CapitalFreezeChoreographer
from core.resilience.extreme_events.models import ExtremeEventClassification, ExtremeEventType
from core.resilience.capital_freeze.models import CapitalControlAction


def test_no_action_under_normal_conditions():
    choreo = CapitalFreezeChoreographer()
    decision = choreo.decide(
        classification=ExtremeEventClassification(
            event_type=ExtremeEventType.NORMAL,
            severity=0.0,
            evidence={},
        )
    )

    assert decision.action == CapitalControlAction.NONE


def test_throttle_on_volatility_spike():
    choreo = CapitalFreezeChoreographer()
    decision = choreo.decide(
        classification=ExtremeEventClassification(
            event_type=ExtremeEventType.VOLATILITY_SPIKE,
            severity=0.7,
            evidence={},
        )
    )

    assert decision.action == CapitalControlAction.THROTTLE_NEW_TRADES


def test_freeze_on_market_crash():
    choreo = CapitalFreezeChoreographer()
    decision = choreo.decide(
        classification=ExtremeEventClassification(
            event_type=ExtremeEventType.MARKET_CRASH,
            severity=0.9,
            evidence={},
        )
    )

    assert decision.action == CapitalControlAction.FREEZE_NEW_TRADES


def test_full_freeze_on_system_anomaly():
    choreo = CapitalFreezeChoreographer()
    decision = choreo.decide(
        classification=ExtremeEventClassification(
            event_type=ExtremeEventType.SYSTEM_ANOMALY,
            severity=0.8,
            evidence={},
        )
    )

    assert decision.action == CapitalControlAction.FULL_SYSTEM_FREEZE
