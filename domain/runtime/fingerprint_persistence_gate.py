from domain.validation.fingerprint_validator import FingerprintValidator
from domain.validation.validation_result import ValidationResult
from domain.behavior_fingerprint.fingerprint import StrategyBehaviorFingerprint


class FingerprintPersistenceGate:
    """
    Prevents invalid fingerprints from being persisted.
    """

    @staticmethod
    def allow_persist(
        fingerprint: StrategyBehaviorFingerprint,
    ) -> ValidationResult:
        return FingerprintValidator.validate(fingerprint)
