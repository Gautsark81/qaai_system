# core/strategy/strategy_registry.py

import json
from pathlib import Path
from dataclasses import asdict
from typing import Dict
from core.strategy.strategy_metadata import StrategyMetadata
from core.strategy.strategy_state import StrategyState


class StrategyRegistry:
    """
    Persistent registry of all strategies.
    """

    def __init__(self, path: str = "data/strategies/registry.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._strategies: Dict[str, StrategyMetadata] = {}
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        raw = json.loads(self.path.read_text())
        for sid, meta in raw.items():
            self._strategies[sid] = StrategyMetadata(
                **meta,
                state=StrategyState(meta["state"]),
            )

    def _persist(self):
        payload = {
            sid: {**asdict(meta), "state": meta.state.value}
            for sid, meta in self._strategies.items()
        }
        self.path.write_text(json.dumps(payload, indent=2))

    def register(self, meta: StrategyMetadata):
        if meta.strategy_id in self._strategies:
            raise RuntimeError("Strategy already registered")
        self._strategies[meta.strategy_id] = meta
        self._persist()

    def promote(self, strategy_id: str, new_state: StrategyState):
        meta = self._strategies[strategy_id]
        self._strategies[strategy_id] = meta.promote(new_state)
        self._persist()

    def get(self, strategy_id: str) -> StrategyMetadata:
        return self._strategies[strategy_id]

    def all(self) -> Dict[str, StrategyMetadata]:
        return self._strategies.copy()
