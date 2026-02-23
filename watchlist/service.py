from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Set

from infra.logging import get_logger

logger = get_logger(__name__)


class WatchlistService:
    """
    Hybrid, dynamic watchlist service.

    - In-memory mapping list_name -> set(symbol)
    - Optional persistence on disk (base_dir/watchlists.json)
    - Can be fed by screeners, manual overrides, etc.
    """

    def __init__(self, base_dir: str | None = None) -> None:
        self._lists: Dict[str, Set[str]] = {}
        self._base_dir = Path(base_dir) if base_dir else None
        if self._base_dir is not None:
            self._base_dir.mkdir(parents=True, exist_ok=True)
            self._load()

    # -------------
    # basic ops
    # -------------
    def add(self, name: str, symbols: Iterable[str]) -> None:
        wl = self._lists.setdefault(name, set())
        before = len(wl)
        wl.update(str(s) for s in symbols)
        after = len(wl)
        logger.info(
            "watchlist_add",
            extra={"watchlist": name, "added": after - before, "wl_size": after},
        )
        self._save()

    def remove(self, name: str, symbols: Iterable[str]) -> None:
        wl = self._lists.get(name)
        if not wl:
            return
        before = len(wl)
        for s in symbols:
            wl.discard(str(s))
        after = len(wl)
        logger.info(
            "watchlist_remove",
            extra={"watchlist": name, "removed": before - after, "wl_size": after},
        )
        self._save()

    def set(self, name: str, symbols: Iterable[str]) -> None:
        self._lists[name] = {str(s) for s in symbols}
        logger.info(
            "watchlist_set",
            extra={"watchlist": name, "wl_size": len(self._lists[name])},
        )
        self._save()

    def get(self, name: str) -> List[str]:
        return sorted(self._lists.get(name, set()))

    def all(self) -> Dict[str, List[str]]:
        return {name: sorted(syms) for name, syms in self._lists.items()}

    # -------------
    # integration helpers
    # -------------
    def update_from_screen(
        self,
        list_name: str,
        screen_results: Iterable["ScreeningResult"],
    ) -> None:
        """
        Replace watchlist with symbols from a screening run.
        """
        from screening.results import ScreeningResult  # local import to avoid cycles

        syms = [r.symbol for r in screen_results if isinstance(r, ScreeningResult)]
        self.set(list_name, syms)

    # -------------
    # persistence
    # -------------
    def _path(self) -> Path | None:
        if self._base_dir is None:
            return None
        return self._base_dir / "watchlists.json"

    def _load(self) -> None:
        path = self._path()
        if path is None or not path.exists():
            return
        try:
            with path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            return
        if not isinstance(raw, dict):
            return
        self._lists = {str(k): set(map(str, v)) for k, v in raw.items() if isinstance(v, list)}

    def _save(self) -> None:
        path = self._path()
        if path is None:
            return
        data = {k: sorted(v) for k, v in self._lists.items()}
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            # don't break trading if disk is flaky
            pass
