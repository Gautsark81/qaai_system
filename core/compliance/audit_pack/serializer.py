import json
from typing import Dict, Any


def serialize_pack(pack) -> bytes:
    def normalize(obj: Any):
        if isinstance(obj, dict):
            return {k: normalize(obj[k]) for k in sorted(obj)}
        if isinstance(obj, list):
            return [normalize(x) for x in obj]
        if hasattr(obj, "__dict__"):
            return normalize(vars(obj))
        return obj

    payload: Dict[str, Any] = {
        "manifest": normalize(pack.manifest),
        "artifacts": normalize(pack.artifacts),
    }

    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
