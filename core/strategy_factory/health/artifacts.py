# core/strategy_factory/health/artifacts.py

from typing import Optional
import hashlib
import json
from dataclasses import dataclass

from .snapshot import StrategyHealthSnapshot
from .version import HEALTH_ENGINE_VERSION
from core.strategy_factory.health.learning.health_learning_context import (
    HealthLearningContext,
)


@dataclass(frozen=True)
class HealthReport:
    """
    Immutable health report produced by the health engine.

    learning_context is OPTIONAL and advisory-only.
    It does not influence scoring, flags, or lifecycle decisions.
    """

    snapshot: StrategyHealthSnapshot
    inputs_hash: str
    learning_context: Optional[HealthLearningContext] = None
    version: str = HEALTH_ENGINE_VERSION

    @staticmethod
    def compute_inputs_hash(inputs: dict) -> str:
        payload = json.dumps(inputs, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()
