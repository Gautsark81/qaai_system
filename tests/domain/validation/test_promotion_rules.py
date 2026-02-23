from domain.validation.promotion_rules import PromotionRules
from domain.behavior_fingerprint.diff import FingerprintDiff


def test_breaking_change_blocks_promotion():
    diff = FingerprintDiff(
        from_version=1,
        to_version=2,
        breaking_changes=["logic"],
        risk_relevant_changes=[],
        execution_relevant_changes=[],
        non_breaking_changes=[],
    )

    res = PromotionRules.can_promote(diff)
    assert res.valid is False
