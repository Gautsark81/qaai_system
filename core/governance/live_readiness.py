from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ReadinessCheck:
    name: str
    passed: bool
    reason: str


@dataclass(frozen=True)
class LiveReadinessReport:
    """
    Immutable, audit-grade readiness report.
    """

    checks: Tuple[ReadinessCheck, ...]

    @property
    def is_live_eligible(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> Tuple[ReadinessCheck, ...]:
        return tuple(c for c in self.checks if not c.passed)


def evaluate_live_readiness(
    *,
    governance_enabled: bool,
    arming_supported: bool,
    capital_safety_enabled: bool,
    telemetry_persistence_enabled: bool,
    replay_available: bool,
    shadow_execution_verified: bool,
    paper_execution_verified: bool,
) -> LiveReadinessReport:
    """
    Evaluate whether the system is eligible for LIVE execution.

    This does NOT enable LIVE.
    It only reports eligibility.
    """

    checks = [
        ReadinessCheck(
            name="Execution governance enforced",
            passed=governance_enabled,
            reason=(
                "Execution governance is active"
                if governance_enabled
                else "Execution governance missing"
            ),
        ),
        ReadinessCheck(
            name="Operator arming & kill switch present",
            passed=arming_supported,
            reason=(
                "Operator arming supported"
                if arming_supported
                else "No operator kill switch"
            ),
        ),
        ReadinessCheck(
            name="Capital safety rails enforced",
            passed=capital_safety_enabled,
            reason=(
                "Capital safety rails active"
                if capital_safety_enabled
                else "Capital safety rails missing"
            ),
        ),
        ReadinessCheck(
            name="Execution telemetry persisted",
            passed=telemetry_persistence_enabled,
            reason=(
                "Telemetry persistence active"
                if telemetry_persistence_enabled
                else "No execution telemetry persistence"
            ),
        ),
        ReadinessCheck(
            name="Execution replay available",
            passed=replay_available,
            reason=(
                "Replay infrastructure available"
                if replay_available
                else "Execution replay unavailable"
            ),
        ),
        ReadinessCheck(
            name="Shadow execution verified",
            passed=shadow_execution_verified,
            reason=(
                "Shadow execution validated"
                if shadow_execution_verified
                else "Shadow execution not verified"
            ),
        ),
        ReadinessCheck(
            name="Paper execution verified",
            passed=paper_execution_verified,
            reason=(
                "Paper execution validated"
                if paper_execution_verified
                else "Paper execution not verified"
            ),
        ),
    ]

    return LiveReadinessReport(checks=tuple(checks))
