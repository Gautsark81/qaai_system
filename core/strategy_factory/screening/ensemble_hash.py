# core/strategy_factory/screening/ensemble_hash.py

from __future__ import annotations
from typing import Iterable
import hashlib
import json

from .ensemble_models import EnsembleSignal


def compute_ensemble_state_hash(
    signals: Iterable[EnsembleSignal],
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