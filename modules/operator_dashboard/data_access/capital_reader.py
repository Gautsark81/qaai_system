from pathlib import Path
from types import SimpleNamespace
import json

BASE_PATH = Path("exports")


class CapitalReader:
    def latest_plan(self):
        files = sorted(BASE_PATH.glob("capital_plan_*.json"))
        if not files:
            return None
        return self._load(files[-1])

    def history(self, strategy_id):
        plan = self.latest_plan()
        if not plan:
            return []
        return [
            a for a in plan.allocations
            if a.strategy_id == strategy_id
        ]

    def _load(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        data["allocations"] = [
            SimpleNamespace(**a) for a in data["allocations"]
        ]
        return SimpleNamespace(**data)
