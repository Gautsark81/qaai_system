from domain.validation.promotion_rules import PromotionRules
from domain.validation.validation_result import ValidationResult
from domain.behavior_fingerprint.diff import FingerprintDiff


class PromotionGate:
    """
    Prevents illegal promotion attempts.
    """

    @staticmethod
    def allow_promotion(
        diff: FingerprintDiff,
    ) -> ValidationResult:
        return PromotionRules.can_promote(diff)
