# core/reproducibility/utils.py

from __future__ import annotations
import hashlib
import json
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_string(data: str) -> str:
    return sha256_bytes(data.encode("utf-8"))


def canonical_json(data: Any) -> str:
    """
    Deterministic JSON serialization.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_json(data: Any) -> str:
    return sha256_string(canonical_json(data))