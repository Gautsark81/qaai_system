from __future__ import annotations


class ResearchExperimentError(RuntimeError):
    """Base exception for all V2.2 research experiment violations."""


class LeakageViolation(ResearchExperimentError):
    """Raised when a research experiment violates leakage rules."""
