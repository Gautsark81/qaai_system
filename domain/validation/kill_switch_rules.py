from domain.validation.validation_result import ValidationResult


class KillSwitchRules:
    """
    Kill-switch invariants.
    Once armed, cannot be ignored.
    """

    @staticmethod
    def validate(
        armed: bool,
        acknowledged: bool,
    ) -> ValidationResult:
        if armed and not acknowledged:
            return ValidationResult.fail(
                "Kill switch armed but not acknowledged"
            )
        return ValidationResult.ok()
