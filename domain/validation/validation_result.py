from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: List[str]

    @staticmethod
    def ok() -> "ValidationResult":
        return ValidationResult(valid=True, errors=[])

    @staticmethod
    def fail(*errors: str) -> "ValidationResult":
        return ValidationResult(valid=False, errors=list(errors))
