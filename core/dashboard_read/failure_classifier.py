from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# ---------------------------------------------------------------------
# SEVERITY LEVELS (LOCKED)
# ---------------------------------------------------------------------

SEVERITY_INFO = "INFO"
SEVERITY_WARN = "WARN"
SEVERITY_ERROR = "ERROR"
SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_FATAL = "FATAL"


# ---------------------------------------------------------------------
# FAILURE CLASSIFICATION MODEL
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class FailureClassification:
    component: str
    severity: str
    error_type: str
    message: str


# ---------------------------------------------------------------------
# ERROR TYPE → SEVERITY MAP (EXPLICIT & DETERMINISTIC)
# ---------------------------------------------------------------------

_ERROR_SEVERITY_MAP: Dict[str, str] = {
    # benign / noise
    "KeyError": SEVERITY_INFO,
    "AttributeError": SEVERITY_INFO,

    # degradations
    "ImportError": SEVERITY_WARN,
    "ModuleNotFoundError": SEVERITY_WARN,
    "TimeoutError": SEVERITY_WARN,

    # functional impact
    "ValueError": SEVERITY_ERROR,
    "RuntimeError": SEVERITY_ERROR,

    # system integrity
    "SnapshotBuildError": SEVERITY_FATAL,
}


# ---------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------

def classify_failure(component: str, error_string: str) -> FailureClassification:
    """
    Deterministically classify a builder-recorded failure string.

    error_string format (guaranteed by builder):
        "<ErrorType>: <message>"
    """

    if ":" in error_string:
        error_type, message = error_string.split(":", 1)
        error_type = error_type.strip()
        message = message.strip()
    else:
        error_type = "UnknownError"
        message = error_string.strip()

    severity = _ERROR_SEVERITY_MAP.get(error_type, SEVERITY_ERROR)

    return FailureClassification(
        component=component,
        severity=severity,
        error_type=error_type,
        message=message,
    )


def classify_all_failures(
    failures: Dict[str, str],
) -> Dict[str, FailureClassification]:
    """
    Classify all failures recorded by the snapshot builder.

    Input:
        {
            "market_state": "RuntimeError: provider down"
        }

    Output:
        {
            "market_state": FailureClassification(...)
        }
    """

    return {
        component: classify_failure(component, error_string)
        for component, error_string in failures.items()
    }
