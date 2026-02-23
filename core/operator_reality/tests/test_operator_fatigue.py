import inspect

from core.operator_reality.fatigue import OperatorFatiguePolicy
from core.operator_reality.intent import OperatorIntentFactory
from core.operator_reality.reconfirmation import OperatorReconfirmationEvaluator
from core.operator_reality.escalation import OperatorEscalationPolicy


def _sample_intent(ts: int = 1000):
    return OperatorIntentFactory.create(
        operator_id="operator-1",
        intent_type="ENABLE_LIVE",
        scope="system",
        timestamp=ts,
        note="fatigue test",
    )


def test_fatigue_policy_warning_and_expiry():
    policy = OperatorFatiguePolicy(
        max_active_seconds=100,
        warning_threshold_seconds=50,
    )

    intent_ts = 1000

    assert policy.is_warning(intent_timestamp=intent_ts, now_timestamp=1050) is True
    assert policy.is_expired(intent_timestamp=intent_ts, now_timestamp=1050) is False

    assert policy.is_expired(intent_timestamp=intent_ts, now_timestamp=1100) is True


def test_reconfirmation_required_on_warning():
    intent = _sample_intent()

    req = OperatorReconfirmationEvaluator.evaluate(
        intent=intent,
        expired=False,
        warning=True,
    )

    assert req.required is True
    assert req.reason == "OPERATOR_FATIGUE_WARNING"


def test_reconfirmation_required_on_expiry():
    intent = _sample_intent()

    req = OperatorReconfirmationEvaluator.evaluate(
        intent=intent,
        expired=True,
        warning=False,
    )

    assert req.required is True
    assert req.reason == "OPERATOR_INTENT_EXPIRED"


def test_no_reconfirmation_when_safe():
    intent = _sample_intent()

    req = OperatorReconfirmationEvaluator.evaluate(
        intent=intent,
        expired=False,
        warning=False,
    )

    assert req.required is False
    assert req.reason == "INTENT_STILL_VALID"


def test_escalation_decision():
    intent = _sample_intent()

    req = OperatorReconfirmationEvaluator.evaluate(
        intent=intent,
        expired=True,
        warning=False,
    )

    esc = OperatorEscalationPolicy.decide(reconfirmation=req)

    assert esc.escalate is True
    assert esc.reason == "OPERATOR_INTENT_EXPIRED"


def test_no_execution_authority_anywhere():
    modules = [
        OperatorFatiguePolicy,
        OperatorReconfirmationEvaluator,
        OperatorEscalationPolicy,
    ]

    forbidden = [
        "execute",
        "order",
        "broker",
        "retry",
        "sleep",
        "while",
        "for ",
        "call(",
    ]

    for obj in modules:
        source = inspect.getsource(obj).lower()
        for word in forbidden:
            assert word not in source
