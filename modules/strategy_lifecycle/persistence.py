# modules/strategy_lifecycle/persistence.py

import json
from pathlib import Path
from typing import Dict

from modules.strategy_lifecycle.store import StrategyLifecycleStore
from modules.strategy_lifecycle.states import StrategyState


class FileBackedLifecycleStore:
    """
    Phase 10 Lifecycle Persistence Adapter (File-backed).

    Responsibilities:
    - Persist lifecycle state to disk
    - Restore state on startup
    - Delegate all logic to StrategyLifecycleStore

    Explicitly NOT responsible for:
    - State transitions
    - Validation
    - Infra orchestration
    """

    def __init__(self, *, path: str):
        self._path = Path(path)
        self._store = StrategyLifecycleStore()

        self._load_from_disk()

    # --------------------------------------------------
    # Persistence
    # --------------------------------------------------

    def _load_from_disk(self) -> None:
        if not self._path.exists():
            return

        data = json.loads(self._path.read_text())

        for strategy_id, state_value in data.items():
            self._store.set_state(
                strategy_id,
                StrategyState(state_value),
            )

    def _persist_to_disk(self) -> None:
        data: Dict[str, str] = {
            strategy_id: state.value
            for strategy_id, state in self._store._state.items()
        }

        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data))

    # --------------------------------------------------
    # Store API (Delegated)
    # --------------------------------------------------

    def get_state(self, strategy_id: str) -> StrategyState:
        return self._store.get_state(strategy_id)

    def set_state(self, strategy_id: str, state: StrategyState) -> None:
        self._store.set_state(strategy_id, state)
        self._persist_to_disk()

    def is_active(self, strategy_id: str) -> bool:
        return self._store.is_active(strategy_id)
