from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Type

from core.v2.research.contracts import ResearchExperimentError
from core.v2.research.experiments.base import (
    ResearchExperiment,
    ExperimentContext,
)
from core.v2.research.datasets.snapshot_loader import SnapshotLoader
from core.v2.research.results import ResearchResult


@dataclass(frozen=True)
class ExperimentSpec:
    """
    Declarative specification of a research experiment.
    """
    experiment_id: str
    experiment_cls: Type[ResearchExperiment]
    dataset_loader: SnapshotLoader
    evaluators: List[str]  # names only (metrics enforced inside experiment)


class ExperimentRegistry:
    """
    Registry and execution gate for V2.2 research experiments.
    """

    def __init__(self):
        self._registry: Dict[str, ExperimentSpec] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, spec: ExperimentSpec) -> None:
        if spec.experiment_id in self._registry:
            raise ResearchExperimentError(
                f"Experiment '{spec.experiment_id}' already registered"
            )

        if not issubclass(spec.experiment_cls, ResearchExperiment):
            raise ResearchExperimentError(
                "experiment_cls must subclass ResearchExperiment"
            )

        self._registry[spec.experiment_id] = spec

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_experiments(self) -> List[str]:
        return sorted(self._registry.keys())

    def get_spec(self, experiment_id: str) -> ExperimentSpec:
        try:
            return self._registry[experiment_id]
        except KeyError:
            raise ResearchExperimentError(
                f"Experiment '{experiment_id}' is not registered"
            )

    # ------------------------------------------------------------------
    # Execution (research-only)
    # ------------------------------------------------------------------

    def run(
        self,
        experiment_id: str,
        *,
        start,
        end,
        seed: int,
        metadata: Dict,
    ) -> ResearchResult:
        """
        Execute a registered research experiment in a fully governed way.
        """
        spec = self.get_spec(experiment_id)

        # Load snapshot (read-only, deterministic)
        snapshot = spec.dataset_loader.load(start, end)

        # Construct immutable experiment context
        ctx = ExperimentContext(
            experiment_id=spec.experiment_id,
            dataset_id=snapshot.dataset_id,
            seed=seed,
            metadata={
                **metadata,
                "snapshot_hash": snapshot.content_hash,
                "start": start.isoformat(),
                "end": end.isoformat(),
            },
        )

        # Instantiate and execute experiment
        experiment = spec.experiment_cls(ctx)
        return experiment.execute()
