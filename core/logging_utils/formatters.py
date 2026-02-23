import json
from typing import Dict, Any


def format_record(record: Dict[str, Any]) -> str:
    return json.dumps(record, separators=(",", ":"), default=str)
