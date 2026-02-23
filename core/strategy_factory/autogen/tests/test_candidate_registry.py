from core.strategy_factory.autogen.candidate_registry import (
    CandidateRegistry,
)
from core.strategy_factory.autogen.candidate_models import (
    CandidateStage,
)


def test_registry_lifecycle_progression():
    registry = CandidateRegistry()

    lab = registry.register_lab_candidate("H1", "hash123")
    assert lab.stage == CandidateStage.LAB

    backtested = registry.update_stage(
        "H1",
        CandidateStage.BACKTESTED,
        ssr=82.0,
        max_drawdown=10.0,
    )

    assert backtested.stage == CandidateStage.BACKTESTED
    assert backtested.ssr == 82.0


def test_registry_append_only():
    registry = CandidateRegistry()

    registry.register_lab_candidate("H1", "hash123")
    registry.update_stage("H1", CandidateStage.BACKTESTED, ssr=80)

    assert len(registry.history()) == 2