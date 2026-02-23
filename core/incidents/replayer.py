import json
from pathlib import Path
from typing import Dict, Any


class IncidentReplayer:
    """
    Read-only loader for incident snapshots.
    Never mutates artifacts.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def load(self, incident_id: str) -> Dict[str, Any]:
        incident_dir = self.base_dir / f"incident_{incident_id}"
        if not incident_dir.exists():
            raise RuntimeError("Incident not found")

        meta_path = incident_dir / "metadata.json"
        if not meta_path.exists():
            raise RuntimeError("Corrupt incident snapshot")

        return json.loads(meta_path.read_text(encoding="utf-8"))

    def modify(self, incident_id: str) -> None:
        """
        Replay is strictly read-only.
        """
        raise RuntimeError("Incident replay is read-only")
