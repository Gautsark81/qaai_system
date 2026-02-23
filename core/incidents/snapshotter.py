import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from uuid import uuid4


class IncidentSnapshotter:
    """
    Captures immutable, forensic snapshots for incidents.
    One snapshot per run_id.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._run_to_incident: Dict[str, str] = {}

    def capture(
        self,
        run_id: str,
        reason: str,
        payload: Dict[str, Any],
    ) -> str:
        # Enforce one snapshot per run
        if run_id in self._run_to_incident:
            raise RuntimeError("Snapshot already exists for this run")

        incident_id = str(uuid4())
        self._run_to_incident[run_id] = incident_id

        incident_dir = self.base_dir / f"incident_{incident_id}"
        incident_dir.mkdir()

        metadata = {
            "incident_id": incident_id,
            "run_id": run_id,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }

        (incident_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8",
        )

        return incident_id
