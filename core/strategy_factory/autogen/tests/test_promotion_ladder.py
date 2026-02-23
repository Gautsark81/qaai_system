from core.strategy_factory.autogen.candidate_registry import CandidateRegistry
from core.strategy_factory.autogen.candidate_models import CandidateStage
from core.strategy_factory.autogen.promotion_ladder import PromotionLadder


def test_promotion_flow():

    registry = CandidateRegistry()
    ladder = PromotionLadder(registry)

    registry.register_lab_candidate("H1", "hash")
    registry.update_stage("H1", CandidateStage.BACKTESTED, ssr=85)
    registry.update_stage("H1", CandidateStage.ROBUST_VALIDATED, ssr=85)

    ladder.promote_to_paper("H1")

    registry.update_stage(
        "H1",
        CandidateStage.PAPER,
        ssr=85,
        shadow_cycles=30,
    )

    ladder.promote_to_shadow("H1")

    ladder.promote_to_live_eligible("H1")

    ladder.promote_to_live("H1", governance_approved=True)

    latest = registry.get_latest("H1")

    assert latest.stage == CandidateStage.LIVE


def test_no_stage_skipping():

    registry = CandidateRegistry()
    ladder = PromotionLadder(registry)

    registry.register_lab_candidate("H2", "hash")

    try:
        ladder.promote_to_paper("H2")
        assert False
    except ValueError:
        assert True