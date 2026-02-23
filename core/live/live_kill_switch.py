# core/live/live_kill_switch.py

import json
from pathlib import Path


class LiveKillSwitch:
    """
    Hierarchical kill switch.
    """

    def __init__(self, path: str = "data/live/kill_switch.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.write_text(
                json.dumps(
                    {
                        "system": False,
                        "strategies": {},
                        "symbols": {},
                    },
                    indent=2,
                )
            )

    def _load(self):
        return json.loads(self.path.read_text())

    def is_killed(
        self,
        strategy_id: str | None = None,
        symbol: str | None = None,
    ) -> bool:
        data = self._load()

        if data["system"]:
            return True
        if strategy_id and data["strategies"].get(strategy_id, False):
            return True
        if symbol and data["symbols"].get(symbol, False):
            return True

        return False
