# core/strategy_factory/screening/meta_alpha_hash.py

from __future__ import annotations
import hashlib
import json
from typing import Iterable

from .meta_alpha_models import MetaAlphaSignal


def compute_meta_alpha_hash(
    signals: Iterable[MetaAlphaSignal],
) -> str:

    payload = [
        {
            "type": s.signal_type,
            "value": str(s.value),
            "description": s.description,
        }
        for s in signals
    ]

    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()