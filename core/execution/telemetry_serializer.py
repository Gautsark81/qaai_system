import json
from dataclasses import asdict
from datetime import datetime

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot


def _default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type not serializable: {type(obj)}")


def serialize_snapshot(snapshot: ExecutionTelemetrySnapshot) -> str:
    """
    Serialize snapshot to a JSON line.
    """
    return json.dumps(asdict(snapshot), default=_default)


def deserialize_snapshot(data: str) -> dict:
    """
    Deserialize JSON line to dict.
    (Rehydration into dataclasses is optional and deferred.)
    """
    return json.loads(data)
