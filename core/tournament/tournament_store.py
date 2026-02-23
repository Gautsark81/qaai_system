# core/tournament/tournament_store.py

import json
from pathlib import Path
from dataclasses import asdict
from core.tournament.tournament_metrics import TournamentMetrics


class TournamentStore:
    def __init__(self, base_path: str = "data/tournament"):
        self.base = Path(base_path)
        self.candidates = self.base / "candidates"
        self.results = self.base / "results"
        self.log = self.base / "promotions.log"

        self.candidates.mkdir(parents=True, exist_ok=True)
        self.results.mkdir(parents=True, exist_ok=True)
        self.log.parent.mkdir(parents=True, exist_ok=True)

    def save_result(
        self,
        strategy_id: str,
        metrics: TournamentMetrics,
    ):
        payload = asdict(metrics)
        path = self.results / f"{strategy_id}.json"
        path.write_text(json.dumps(payload, indent=2))

    def log_promotion(self, line: str):
        with self.log.open("a") as f:
            f.write(line + "\n")
