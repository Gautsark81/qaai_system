import json
from pathlib import Path
from typing import List

from core.operations.ops_events import OpsEvent


class OpsEventStore:
    """
    Append-only store for operational events (Phase O-1).
    """

    def __init__(self, root_dir: Path | str = "ops_events"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def append(self, event: OpsEvent) -> None:
        path = self.root / f"{event.event_type}.jsonl"

        with open(path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "event_type": event.event_type,
                        "operator": event.operator,
                        "notes": event.notes,
                        "occurred_at": event.occurred_at.isoformat(),
                    }
                )
                + "\n"
            )

    def load(self, event_type: str) -> List[dict]:
        path = self.root / f"{event_type}.jsonl"
        if not path.exists():
            return []

        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def load_all(self) -> List[dict]:
        """
        Load all operational events across all event types.
        Read-only aggregation for dashboards & intelligence layers.
        """
        events: List[dict] = []

        for path in self.root.glob("*.jsonl"):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    events.append(json.loads(line))

        return events
