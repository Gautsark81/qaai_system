# core/dashboard_read/verification/report.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class VerificationIssue:
    code: str
    message: str


@dataclass(frozen=True)
class VerificationReport:
    is_valid: bool
    issues: List[VerificationIssue]

    @staticmethod
    def success() -> "VerificationReport":
        return VerificationReport(is_valid=True, issues=[])

    @staticmethod
    def failure(issues: List[VerificationIssue]) -> "VerificationReport":
        return VerificationReport(is_valid=False, issues=issues)
