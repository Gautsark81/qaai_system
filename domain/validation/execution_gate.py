from domain.validation.validation_result import ValidationResult


class ExecutionGate:
    """
    Final execution gate.
    No execution may pass if validation fails.
    """

    @staticmethod
    def allow_execution(
        fingerprint_valid: bool,
        promotion_allowed: bool,
        kill_switch_clear: bool,
    ) -> ValidationResult:
        if not fingerprint_valid:
            return ValidationResult.fail("Fingerprint validation failed")

        if not promotion_allowed:
            return ValidationResult.fail("Promotion rules blocked execution")

        if not kill_switch_clear:
            return ValidationResult.fail("Kill switch active")

        return ValidationResult.ok()
