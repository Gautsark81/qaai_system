from domain.validation.execution_gate import ExecutionGate
from domain.validation.validation_result import ValidationResult


class RuntimeGate:
    """
    Central runtime enforcement point.
    No execution logic allowed.
    """

    @staticmethod
    def check_execution(
        *,
        fingerprint_valid: bool,
        promotion_allowed: bool,
        kill_switch_clear: bool,
    ) -> ValidationResult:
        return ExecutionGate.allow_execution(
            fingerprint_valid=fingerprint_valid,
            promotion_allowed=promotion_allowed,
            kill_switch_clear=kill_switch_clear,
        )
