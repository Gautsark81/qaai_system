from enum import Enum


class SeverityLevel(str, Enum):
    """
    Canonical severity levels for oversight findings.

    Ordering is intentional and MUST remain stable
    for correlation, escalation, and dashboards.
    """

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    @classmethod
    def ordered(cls) -> list["SeverityLevel"]:
        """
        Deterministic severity ordering from lowest to highest.
        """
        return [
            cls.INFO,
            cls.WARNING,
            cls.CRITICAL,
        ]
