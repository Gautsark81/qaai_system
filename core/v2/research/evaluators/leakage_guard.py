from __future__ import annotations

import inspect
from typing import Iterable, Type, TYPE_CHECKING

from core.v2.research.contracts import LeakageViolation

if TYPE_CHECKING:
    from core.v2.research.experiments.base import ResearchExperiment


class LeakageGuard:
    """
    Enforces research-time safety invariants.
    """

    _BANNED_IMPORT_KEYWORDS: Iterable[str] = (
        "execution",
        "order_manager",
        "broker",
        "capital",
        "live_trading",
        "orchestrator",
    )

    def assert_safe(self, experiment: "ResearchExperiment") -> None:
        self._assert_lifecycle_integrity(experiment)
        self._assert_no_forbidden_imports(experiment)

    def _assert_lifecycle_integrity(self, experiment: object) -> None:
        if getattr(experiment, "_ran", False):
            raise LeakageViolation("Experiment already executed run()")
        if getattr(experiment, "_evaluated", False):
            raise LeakageViolation("Experiment already executed evaluate()")

    def _assert_no_forbidden_imports(self, experiment: object) -> None:
        source = self._safe_get_source(experiment.__class__)
        for keyword in self._BANNED_IMPORT_KEYWORDS:
            if keyword in source:
                raise LeakageViolation(
                    f"Forbidden dependency detected: '{keyword}'"
                )

    @staticmethod
    def _safe_get_source(cls: Type) -> str:
        try:
            return inspect.getsource(cls)
        except (OSError, IOError):
            raise LeakageViolation(
                "Unable to inspect experiment source"
            )
