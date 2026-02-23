# core/strategy_factory/autogen/hypothesis_models.py

from dataclasses import dataclass
from typing import Dict
import hashlib
import json


@dataclass(frozen=True)
class StrategyHypothesis:
    hypothesis_id: str
    version: int
    feature_set: Dict[str, float]
    entry_logic: str
    exit_logic: str
    timeframe: str
    regime_target: str

    def compute_hash(self) -> str:
        payload = {
            "version": self.version,
            "feature_set": dict(sorted(self.feature_set.items())),
            "entry_logic": self.entry_logic,
            "exit_logic": self.exit_logic,
            "timeframe": self.timeframe,
            "regime_target": self.regime_target,
        }
        encoded = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()