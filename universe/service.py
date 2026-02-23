# universe/service.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set


@dataclass(slots=True)
class SymbolMetadata:
    symbol: str
    sector: str
    segment: str = "EQ"   # e.g. EQ, FNO, ETF
    active: bool = True
    meta: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # dataclasses.asdict will deepcopy meta; ensure not None for JSON
        if d["meta"] is None:
            d["meta"] = {}
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolMetadata":
        return cls(
            symbol=str(data["symbol"]),
            sector=str(data["sector"]),
            segment=str(data.get("segment", "EQ")),
            active=bool(data.get("active", True)),
            meta=dict(data.get("meta", {})),
        )


class UniverseService:
    """
    Sector-aware universe manager.

    Supercharged:
      - Track sector/segment/flags per symbol
      - Fast sector-based universe slices
      - Can persist metadata to disk for reuse

    Hybrid:
      - In-memory for fast operations
      - Optional JSON persistence (base_dir/universe.json)

    Dynamic:
      - Add / update / deactivate symbols
      - Filter universes by sectors, segments, includes/excludes
    """

    _FILENAME = "universe.json"

    def __init__(self, base_dir: Optional[str] = None) -> None:
        self._meta: Dict[str, SymbolMetadata] = {}
        self._base_dir = Path(base_dir) if base_dir else None
        if self._base_dir is not None:
            self._base_dir.mkdir(parents=True, exist_ok=True)
            self._load()

    # ----------------
    # Internal helpers
    # ----------------
    def _path(self) -> Optional[Path]:
        if self._base_dir is None:
            return None
        return self._base_dir / self._FILENAME

    def _load(self) -> None:
        path = self._path()
        if path is None or not path.exists():
            return
        try:
            with path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            return
        if not isinstance(raw, list):
            return
        self._meta.clear()
        for item in raw:
            try:
                md = SymbolMetadata.from_dict(item)
            except Exception:
                continue
            self._meta[md.symbol] = md

    def _save(self) -> None:
        path = self._path()
        if path is None:
            return
        data = [md.to_dict() for md in self._meta.values()]
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            # don't break trading on disk issues
            pass

    # -----------
    # CRUD
    # -----------
    def upsert_symbol(
        self,
        symbol: str,
        *,
        sector: str,
        segment: str = "EQ",
        active: bool = True,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Insert or update symbol metadata.
        """
        symbol = str(symbol)
        if symbol in self._meta:
            md = self._meta[symbol]
            md.sector = sector
            md.segment = segment
            md.active = active
            if meta is not None:
                # merge
                if md.meta is None:
                    md.meta = dict(meta)
                else:
                    md.meta.update(meta)
        else:
            self._meta[symbol] = SymbolMetadata(
                symbol=symbol,
                sector=sector,
                segment=segment,
                active=active,
                meta=dict(meta or {}),
            )
        self._save()

    def deactivate(self, symbol: str) -> None:
        if symbol in self._meta:
            self._meta[symbol].active = False
            self._save()

    # -----------
    # Queries
    # -----------
    def metadata(self, symbol: str) -> Optional[SymbolMetadata]:
        return self._meta.get(symbol)

    def sector(self, symbol: str) -> Optional[str]:
        md = self._meta.get(symbol)
        return md.sector if md else None

    def all_symbols(self, *, active_only: bool = True) -> List[str]:
        if active_only:
            return sorted(s for s, md in self._meta.items() if md.active)
        return sorted(self._meta.keys())

    def universe_by_sector(
        self,
        sectors: Iterable[str],
        *,
        segment: Optional[str] = None,
        active_only: bool = True,
    ) -> List[str]:
        sector_set = {str(s).upper() for s in sectors}
        out: List[str] = []
        for symbol, md in self._meta.items():
            if active_only and not md.active:
                continue
            if md.sector.upper() not in sector_set:
                continue
            if segment is not None and md.segment != segment:
                continue
            out.append(symbol)
        return sorted(out)

    def filter_symbols(
        self,
        symbols: Iterable[str],
        *,
        include_sectors: Optional[Iterable[str]] = None,
        exclude_sectors: Optional[Iterable[str]] = None,
        require_active: bool = True,
    ) -> List[str]:
        """
        Filter a list of symbols by sector constraints.

        include_sectors: if provided, keep only symbols whose sector is in this set.
        exclude_sectors: if provided, drop symbols whose sector is in this set.
        """
        include_set: Optional[Set[str]] = (
            {s.upper() for s in include_sectors} if include_sectors else None
        )
        exclude_set: Optional[Set[str]] = (
            {s.upper() for s in exclude_sectors} if exclude_sectors else None
        )

        out: List[str] = []
        for sym in symbols:
            md = self._meta.get(sym)
            if md is None:
                continue
            if require_active and not md.active:
                continue
            sec = md.sector.upper()
            if include_set is not None and sec not in include_set:
                continue
            if exclude_set is not None and sec in exclude_set:
                continue
            out.append(sym)
        return sorted(set(out))
