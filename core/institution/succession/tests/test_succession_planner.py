from core.institution.succession.models import Steward
from core.institution.succession.planner import SuccessionPlanner


def test_initial_steward():
    founder = Steward("S1", "Founder", {})
    planner = SuccessionPlanner(initial_steward=founder)

    assert planner.current_steward() == founder
    assert planner.history() == []


def test_handover_creates_event():
    founder = Steward("S1", "Founder", {})
    successor = Steward("S2", "Successor", {})

    planner = SuccessionPlanner(initial_steward=founder)
    event = planner.handover(to_steward=successor, reason="planned succession")

    assert planner.current_steward() == successor
    assert event.from_steward == founder
    assert event.to_steward == successor


def test_multiple_successions_recorded():
    s1 = Steward("S1", "Founder", {})
    s2 = Steward("S2", "CTO", {})
    s3 = Steward("S3", "Board", {})

    planner = SuccessionPlanner(initial_steward=s1)
    planner.handover(to_steward=s2, reason="role change")
    planner.handover(to_steward=s3, reason="governance transition")

    history = planner.history()
    assert len(history) == 2
    assert history[0].from_steward == s1
    assert history[1].to_steward == s3
