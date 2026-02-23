from pathlib import Path
from types import SimpleNamespace
import json

BASE_PATH = Path("tournament/results")


class TournamentReader:
    def all_history(self):
        if not BASE_PATH.exists():
            return []
        rows = []
        for f in BASE_PATH.glob("*.json"):
            with open(f) as fh:
                for r in json.load(fh):
                    rows.append(SimpleNamespace(**r))
        return rows

    def history(self, strategy_id):
        return [
            r for r in self.all_history()
            if r.strategy_id == strategy_id
        ]
