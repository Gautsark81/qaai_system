# core/observability/event_store.py

import json
from pathlib import Path
from dataclasses import asdict
from core.observability.event import Event


class EventStore:
    """
    Append-only event store.
    """

    def __init__(self, path: str = "data/events/events.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Event):
        with self.path.open("a") as f:
            f.write(json.dumps(asdict(event)) + "\n")

    def load_all(self):
        if not self.path.exists():
            return []
        return [
            json.loads(line)
            for line in self.path.read_text().splitlines()
        ]
