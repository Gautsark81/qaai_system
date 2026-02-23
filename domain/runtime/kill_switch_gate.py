from domain.validation.kill_switch_rules import KillSwitchRules
from domain.validation.validation_result import ValidationResult


class KillSwitchGate:
    """
    Enforces kill-switch acknowledgement.
    """

    @staticmethod
    def allow_execution(
        *,
        armed: bool,
        acknowledged: bool,
    ) -> ValidationResult:
        return KillSwitchRules.validate(
            armed=armed,
            acknowledged=acknowledged,
        )
