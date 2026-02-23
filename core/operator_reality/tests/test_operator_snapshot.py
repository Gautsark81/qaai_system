import inspect

from core.operator_reality.snapshot_builder import OperatorSnapshotBuilder
from core.operator_reality.intent import OperatorIntentFactory
from core.operator_reality.snapshot import OperatorSnapshot


def _sample_intent():
    return OperatorIntentFactory.create(
        operator_id="operator-1",
        intent_type="ENABLE_LIVE",
        scope="system",
        timestamp=1000,
        note="snapshot test",
    )


def test_operator_snapshot_is_created():
    intent = _sample_intent()

    snapshot = OperatorSnapshotBuilder.build(
        timestamp=2000,
        mode="live",
        strategy_id="strat-123",
        last_intent=intent,
        governance_checks={
            "risk": "passed",
            "capital": "within_limits",
            "kill_switch": "armed",
        },
        capital_view={
            "allocated": "10%",
            "max_allowed": "15%",
        },
        notes="market open",
    )

    assert isinstance(snapshot, OperatorSnapshot)
    assert snapshot.mode == "live"
    assert snapshot.strategy_id == "strat-123"
    assert snapshot.last_operator_intent == "ENABLE_LIVE"
    assert snapshot.governance_summary["risk"] == "passed"


def test_operator_snapshot_is_deterministic():
    intent = _sample_intent()

    s1 = OperatorSnapshotBuilder.build(
        timestamp=2000,
        mode="paper",
        strategy_id=None,
        last_intent=intent,
        governance_checks={},
        capital_view={},
    )

    s2 = OperatorSnapshotBuilder.build(
        timestamp=2000,
        mode="paper",
        strategy_id=None,
        last_intent=intent,
        governance_checks={},
        capital_view={},
    )

    assert s1 == s2


def test_snapshot_does_not_mutate_inputs():
    intent = _sample_intent()
    gov = {"risk": "passed"}
    cap = {"allocated": "5%"}

    _ = OperatorSnapshotBuilder.build(
        timestamp=3000,
        mode="shadow",
        strategy_id=None,
        last_intent=intent,
        governance_checks=gov,
        capital_view=cap,
    )

    assert gov == {"risk": "passed"}
    assert cap == {"allocated": "5%"}


def test_no_execution_authority_present():
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

    source = inspect.getsource(OperatorSnapshotBuilder).lower()
    for word in forbidden:
        assert word not in source
