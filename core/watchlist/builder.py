from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Any, Optional, Iterator
from datetime import datetime, timezone
from pathlib import Path
import json
import pandas as pd

from core.watchlist.filters import filter_passed, filter_min_score
from core.watchlist.models import WatchlistManifest

# 🔑 SINGLE SOURCE OF TRUTH (CRITICAL)
from core.live_ops.watchlist import WatchlistEntry
from core.contracts.screening import ScreeningResult


# ======================================================================
# Internal normalized contract
# ======================================================================

@dataclass(frozen=True)
class _NormalizedResult:
    symbol: str
    score: float
    reasons: List[str]


# ======================================================================
# PUBLIC RESULT ADAPTER
# ======================================================================

class WatchlistResult:
    """
    Unified return object.

    Behaves as:
    - list (len, iter)
    - manifest (.entries)
    - snapshot (.iloc)
    """

    def __init__(self, manifest: WatchlistManifest):
        self.manifest = manifest
        self.entries = manifest.entries

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterator[WatchlistEntry]:
        return iter(self.entries)

    def __getitem__(self, idx):
        return self.entries[idx]

    @property
    def iloc(self):
        return pd.DataFrame(
            [
                {
                    "symbol": e.symbol,
                    "rank": e.rank,
                    "confidence": e.confidence,
                    "source": e.source,
                }
                for e in self.entries
            ]
        ).iloc


# ======================================================================
# Canonical Watchlist Builder
# ======================================================================

class WatchlistBuilder:
    """
    Canonical Watchlist Builder.

    HARD LAW:
    - Same input → same output
    - No implicit wall-clock dependency
    """

    _DETERMINISTIC_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def __init__(
        self,
        max_symbols: Optional[int] = None,
        min_score: float = 0.0,
        source: str = "screening",
        *,
        generated_at: Optional[datetime] = None,
    ):
        self.max_symbols = max_symbols
        self.min_score = float(min_score)
        self.source = source

        # 🔒 Deterministic by default (NEVER None)
        self.generated_at = generated_at or self._DETERMINISTIC_EPOCH

    def build(self, results: Iterable[Any]) -> WatchlistManifest:
        results = list(results)

        passed = filter_passed(results)
        qualified = filter_min_score(passed, self.min_score)

        normalized = [self._normalize(r) for r in qualified]
        normalized.sort(key=lambda r: (-r.score, r.symbol))

        if self.max_symbols is not None:
            normalized = normalized[: self.max_symbols]

        max_score = max((r.score for r in normalized), default=1.0) or 1.0

        entries: List[WatchlistEntry] = []
        for rank, r in enumerate(normalized, start=1):
            entries.append(
                WatchlistEntry(
                    symbol=r.symbol,
                    rank=rank,
                    confidence=round(r.score / max_score, 4),
                    source=self.source,
                    reasons=r.reasons,
                )
            )

        # 🔒 CRITICAL: always inject generated_at explicitly
        return WatchlistManifest(
            generated_at=self.generated_at,
            entries=entries,
            constraints={
                "max_symbols": self.max_symbols,
                "min_score": self.min_score,
                "input_count": len(results),
                "final_count": len(entries),
            },
        )

    def _normalize(self, obj: Any) -> _NormalizedResult:
        if isinstance(obj, ScreeningResult):
            return _NormalizedResult(
                symbol=obj.symbol,
                score=float(obj.score or 0.0),
                reasons=list(getattr(obj, "reasons", [])),
            )

        if hasattr(obj, "symbol"):
            return _NormalizedResult(
                symbol=str(obj.symbol),
                score=float(getattr(obj, "score", 1.0)),
                reasons=list(getattr(obj, "failed_rules", [])),
            )

        if isinstance(obj, tuple) and len(obj) == 2:
            return _NormalizedResult(str(obj[0]), float(obj[1]), [])

        if isinstance(obj, str):
            return _NormalizedResult(obj, 1.0, [])

        raise TypeError(f"Unsupported screening result type: {type(obj)}")


# ======================================================================
# PUBLIC HELPERS (FINAL CONTRACT)
# ======================================================================

def build_watchlist(
    screening_results: Iterable[Any],
    max_symbols: Optional[int] = None,
    min_score: float = 0.0,
) -> WatchlistResult:
    manifest = WatchlistBuilder(
        max_symbols=max_symbols,
        min_score=min_score,
    ).build(screening_results)
    return WatchlistResult(manifest)


def build_watchlist_manifest(
    screening_results: Iterable[Any],
    max_symbols: Optional[int] = None,
    min_score: float = 0.0,
) -> WatchlistManifest:
    return WatchlistBuilder(
        max_symbols=max_symbols,
        min_score=min_score,
    ).build(screening_results)


# ======================================================================
# Legacy persistence (INTENTIONALLY NON-DETERMINISTIC)
# ======================================================================

def build_and_persist_watchlist(*args, **kwargs) -> WatchlistManifest:
    screening_results = args[0]
    path = Path(args[2]) if len(args) >= 3 else None

    # 👇 persistence SHOULD reflect real time
    manifest = WatchlistBuilder(
        max_symbols=kwargs.get("max_symbols"),
        min_score=kwargs.get("min_score", 0.0),
        generated_at=datetime.now(timezone.utc),
    ).build(screening_results)

    if path:
        _persist_manifest_atomic(manifest, path)

    return manifest


def _persist_manifest_atomic(manifest: WatchlistManifest, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")

    payload = {
        "generated_at": manifest.generated_at.isoformat(),
        "constraints": manifest.constraints,
        "entries": [
            {
                "symbol": e.symbol,
                "rank": e.rank,
                "confidence": e.confidence,
                "source": e.source,
                "reasons": e.reasons,
            }
            for e in manifest.entries
        ],
    }

    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    tmp.replace(path)
