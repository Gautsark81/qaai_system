# core/strategy_factory/screening/screening_hash.py

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Iterable

from .screening_models import ScreeningScore


def _normalize_decimal(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.00000001")), "f")


def compute_screening_state_hash(
    scores: Iterable[ScreeningScore],
) -> str:
    """
    Deterministic order-independent hash.

    - Sort by strategy_dna
    - Normalize decimals
    """

    normalized = []

    for s in sorted(scores, key=lambda x: x.strategy_dna):
        normalized.append(
            {
                "strategy_dna": s.strategy_dna,
                "score": _normalize_decimal(s.score),
                "rank": s.rank,
                "metrics_hash": s.metrics_hash,
            }
        )

    payload = json.dumps(normalized, sort_keys=True)

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()