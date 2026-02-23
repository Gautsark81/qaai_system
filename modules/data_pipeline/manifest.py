# modules/data_pipeline/manifest.py
from __future__ import annotations
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import json


def checksum_of_rows_for_manifest_symbol(rows: int, symbol: str, date: str) -> str:
    s = f"{symbol}|{date}|{rows}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def make_manifest(symbol: str, rows: int, date: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    manifest = {
        "symbol": symbol,
        "rows": int(rows),
        "date": date,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "checksum": checksum_of_rows_for_manifest_symbol(rows, symbol, date),
    }
    if extra:
        manifest["extra"] = extra
    return manifest


def validate_manifest(manifest: Dict[str, Any]) -> bool:
    required = {"symbol", "rows", "date", "created_at", "checksum"}
    if not required.issubset(set(manifest.keys())):
        return False
    expected = checksum_of_rows_for_manifest_symbol(manifest["rows"], manifest["symbol"], manifest["date"])
    return manifest.get("checksum") == expected
