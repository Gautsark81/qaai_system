from domain.validation.validation_result import ValidationResult


class SSRAdmissionRules:
    """
    Governs strategy eligibility based on SSR.
    """

    MIN_SSR = 0.80

    @staticmethod
    def validate(ssr: float) -> ValidationResult:
        if ssr < SSRAdmissionRules.MIN_SSR:
            return ValidationResult.fail(
                f"SSR {ssr:.2f} below minimum {SSRAdmissionRules.MIN_SSR:.2f}"
            )
        return ValidationResult.ok()
