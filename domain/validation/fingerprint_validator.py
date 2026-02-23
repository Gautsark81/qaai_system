from domain.validation.validation_result import ValidationResult
from domain.behavior_fingerprint.fingerprint import StrategyBehaviorFingerprint


class FingerprintValidator:
    """
    Constitutional validator for StrategyBehaviorFingerprint.
    No execution logic allowed.
    """

    @staticmethod
    def validate(fp: StrategyBehaviorFingerprint) -> ValidationResult:
        errors = []

        # ---- Identity ----
        if not fp.identity.strategy_id:
            errors.append("Missing strategy_id")

        if not fp.identity.code_hash:
            errors.append("Missing code_hash")

        # ---- Risk dominance ----
        if fp.risk_behavior.max_position_pct <= 0:
            errors.append("Invalid max_position_pct")

        if fp.risk_behavior.capital_concentration > 0.25:
            errors.append("Capital concentration exceeds hard limit")

        # ---- Execution sanity ----
        if fp.execution_behavior.latency_tolerance_ms <= 0:
            errors.append("Invalid latency tolerance")

        # ---- Governance ----
        if fp.governance_flags.kill_switch_required and not fp.governance_flags.allowed_environments:
            errors.append("Kill switch armed but no allowed environments")

        return (
            ValidationResult.ok()
            if not errors
            else ValidationResult.fail(*errors)
        )
