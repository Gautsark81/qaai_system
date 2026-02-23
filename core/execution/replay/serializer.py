import json
from dataclasses import asdict
from datetime import datetime


def _default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type not serializable: {type(obj)}")


def serialize(obj) -> str:
    """
    Serialize dataclass-like objects to JSON line.
    """
    return json.dumps(asdict(obj), default=_default)


def deserialize(line: str) -> dict:
    """
    Deserialize JSON line to dict.
    Rehydration into dataclasses is deferred.
    """
    return json.loads(line)
