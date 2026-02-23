from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReplayFailure:
    """
    Base class for all replay failures.

    Failures are data, not exceptions.
    """
    reason: str


@dataclass(frozen=True)
class IntegrityFailure(ReplayFailure):
    pass


@dataclass(frozen=True)
class SchemaMismatch(ReplayFailure):
    pass


@dataclass(frozen=True)
class MissingEvidence(ReplayFailure):
    pass


@dataclass(frozen=True)
class ReplayInvariantViolation(ReplayFailure):
    pass


@dataclass(frozen=True)
class UnsupportedReplay(ReplayFailure):
    pass