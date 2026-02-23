import inspect

from core.incident_governance.incident_types import IncidentType
from core.incident_governance.incident_record import IncidentRecord
from core.incident_governance.kill_hierarchy import KillHierarchyPolicy, KillDecision
from core.incident_governance.postmortem import PostMortemHook


def test_incident_record_creation():
    record = IncidentRecord(
        incident_type=IncidentType.DATA_INTEGRITY,
        timestamp=1000,
        scope="execution",
        summary={"issue": "checksum mismatch"},
    )

    assert record.incident_type == IncidentType.DATA_INTEGRITY
    assert record.scope == "execution"


def test_kill_decision_hard_kill():
    decision = KillHierarchyPolicy.decide(
        incident_type=IncidentType.CAPITAL_BREACH
    )

    assert isinstance(decision, KillDecision)
    assert decision.escalate is True
    assert decision.authority == "HARD_KILL"


def test_kill_decision_soft_kill():
    decision = KillHierarchyPolicy.decide(
        incident_type=IncidentType.OPERATOR_ABSENCE
    )

    assert decision.authority == "SOFT_KILL"


def test_non_fatal_incident():
    decision = KillHierarchyPolicy.decide(
        incident_type=IncidentType.EXTERNAL_DEPENDENCY
    )

    assert decision.escalate is False


def test_postmortem_hook_creation():
    record = IncidentRecord(
        incident_type=IncidentType.GOVERNANCE_VIOLATION,
        timestamp=2000,
        scope="governance",
        summary={"rule": "no silent execution"},
    )

    hook = PostMortemHook(
        incident=record,
        notes={"action": "review required"},
    )

    assert hook.incident == record


def test_no_execution_authority_present():
    modules = [
        KillHierarchyPolicy,
        IncidentRecord,
        PostMortemHook,
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
