from domain.runtime.runtime_gate import RuntimeGate
from domain.validation.validation_result import ValidationResult


class ExecutionEntryGate:
    """
    Final execution barrier.
    All runtime paths must pass here.
    """

    @staticmethod
    def allow(
        *,
        fingerprint_valid: bool,
        promotion_allowed: bool,
        kill_switch_clear: bool,
    ) -> ValidationResult:
        return RuntimeGate.check_execution(
            fingerprint_valid=fingerprint_valid,
            promotion_allowed=promotion_allowed,
            kill_switch_clear=kill_switch_clear,
        )
