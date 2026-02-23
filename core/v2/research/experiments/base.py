from __future__ import annotations

import abc
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, final

from core.v2.research.contracts import ResearchExperimentError
from core.v2.research.results import ResearchResult
from core.v2.research.evaluators.leakage_guard import LeakageGuard


@dataclass(frozen=True)
class ExperimentContext:
    """
    Immutable context for a research experiment.
    Enforces determinism and traceability.
    """
    experiment_id: str
    dataset_id: str
    seed: int
    metadata: Dict[str, Any]


class ResearchExperiment(abc.ABC):
    """
    Abstract base class for ALL V2.2 research experiments.
    """

    def __init__(self, context: ExperimentContext):
        self._context = context
        self._leakage_guard = LeakageGuard()
        self._loaded = False
        self._ran = False
        self._evaluated = False

    # ------------------------------------------------------------------
    # Required overrides
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def load(self) -> None: ...

    @abc.abstractmethod
    def run(self) -> Any: ...

    @abc.abstractmethod
    def evaluate(self, raw_result: Any) -> Dict[str, Any]: ...

    # ------------------------------------------------------------------
    # Lifecycle orchestration (DO NOT OVERRIDE)
    # ------------------------------------------------------------------

    @final
    def execute(self) -> ResearchResult:
        self._validate_context()

        if self._loaded or self._ran or self._evaluated:
            raise ResearchExperimentError(
                "Experiment instances are single-use"
            )

        self.load()
        self._loaded = True

        self._leakage_guard.assert_safe(self)

        raw = self.run()
        self._ran = True

        metrics = self.evaluate(raw)
        self._evaluated = True

        return self._finalize(raw, metrics)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _validate_context(self) -> None:
        if not self._context.experiment_id:
            raise ResearchExperimentError("experiment_id is required")
        if not self._context.dataset_id:
            raise ResearchExperimentError("dataset_id is required")

    def _finalize(self, raw: Any, metrics: Dict[str, Any]) -> ResearchResult:
        return ResearchResult(
            experiment_id=self._context.experiment_id,
            dataset_id=self._context.dataset_id,
            seed=self._context.seed,
            metrics=metrics,
            payload_hash=self._hash_payload(raw, metrics),
            metadata=self._context.metadata,
        )

    @staticmethod
    def _hash_payload(raw: Any, metrics: Dict[str, Any]) -> str:
        h = hashlib.sha256()
        h.update(repr(raw).encode())
        h.update(repr(metrics).encode())
        return h.hexdigest()

    @property
    def context(self) -> ExperimentContext:
        return self._context
