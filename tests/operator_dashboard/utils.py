from dataclasses import asdict
from datetime import datetime
from typing import Any


def normalize(obj: Any):
    """
    Remove volatile fields for snapshot stability.
    """
    if isinstance(obj, dict):
        return {
            k: normalize(v)
            for k, v in obj.items()
            if k not in {"timestamp", "updated_at", "decided_at"}
        }
    if isinstance(obj, list):
        return [normalize(x) for x in obj]
    if hasattr(obj, "__dict__"):
        return normalize(asdict(obj))
    if isinstance(obj, datetime):
        return "<DATETIME>"
    return obj
