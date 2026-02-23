from domain.runtime.promotion_gate import PromotionGate
from domain.behavior_fingerprint.diff import FingerprintDiff


def test_runtime_promotion_gate_blocks_breaking_change():
    diff = FingerprintDiff(
        from_version=1,
        to_version=2,
        breaking_changes=["logic"],
        risk_relevant_changes=[],
        execution_relevant_changes=[],
        non_breaking_changes=[],
    )

    res = PromotionGate.allow_promotion(diff)
    assert res.valid is False
