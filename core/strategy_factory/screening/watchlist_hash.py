# core/strategy_factory/screening/watchlist_hash.py

from __future__ import annotations
import hashlib
import json
from typing import Iterable

from .watchlist_models import WatchlistEntry


def compute_watchlist_hash(
    entries: Iterable[WatchlistEntry],
    recommended_size: int,
) -> str:

    payload = {
        "entries": [
            {"dna": e.strategy_dna, "rank": e.rank}
            for e in entries
        ],
        "recommended_size": recommended_size,
    }

    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()