from domain.validation.validation_result import ValidationResult
from domain.behavior_fingerprint.diff import FingerprintDiff


class PromotionRules:
    """
    Hard promotion invariants.
    ML, PnL, SSR cannot override these.
    """

    @staticmethod
    def can_promote(diff: FingerprintDiff) -> ValidationResult:
        if diff.breaking_changes:
            return ValidationResult.fail(
                "Breaking fingerprint change blocks promotion"
            )

        if diff.risk_relevant_changes:
            return ValidationResult.fail(
                "Risk-relevant fingerprint change blocks promotion"
            )

        return ValidationResult.ok()
