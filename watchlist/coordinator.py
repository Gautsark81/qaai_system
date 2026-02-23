# watchlist/coordinator.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from screening.results import ScreeningResult
from watchlist.service import WatchlistService


@dataclass(slots=True)
class CoordinationRule:
    """
    How to map a screen into a watchlist.

    source_screen: name of the screen (ScreenConfig.name)
    target_watchlist: watchlist name to update
    mode:
      - "replace": overwrite target watchlist with new symbols
      - "union":   union with existing symbols
      - "intersection": keep only symbols that are both existing and in new results
    max_symbols: optional cap on number of symbols
    min_score:   optional minimum score to be included
    """

    source_screen: str
    target_watchlist: str
    mode: str = "replace"  # replace | union | intersection
    max_symbols: Optional[int] = None
    min_score: Optional[float] = None


class WatchlistCoordinator:
    """
    Supercharged multi-watchlist coordination.

    - Build multiple lists from multiple screens in one shot.
    - Apply different modes per list (replace / union / intersection).
    - Enforce symbol priority across lists (so a symbol appears only in its
      highest-priority list, e.g. LONG_CORE > SECONDARY > OBSERVE).
    """

    def __init__(self, watchlists: WatchlistService) -> None:
        self._wl = watchlists

    # -----------------------
    # Rule application
    # -----------------------
    def apply_rules(
        self,
        results_by_screen: Mapping[str, Sequence[ScreeningResult]],
        rules: Sequence[CoordinationRule],
    ) -> None:
        """
        Apply rules mapping screen results into watchlists.

        This does not enforce cross-list uniqueness/piority; call
        enforce_priority afterwards if you want that.
        """
        for rule in rules:
            screen_results = list(results_by_screen.get(rule.source_screen, []))
            if not screen_results:
                continue

            # filter by min_score
            if rule.min_score is not None:
                screen_results = [
                    r for r in screen_results if r.score >= rule.min_score
                ]

            # apply max_symbols (results already sorted by ScreeningEngine)
            if rule.max_symbols is not None and rule.max_symbols > 0:
                screen_results = screen_results[: rule.max_symbols]

            symbols = [r.symbol for r in screen_results]

            existing = set(self._wl.get(rule.target_watchlist))

            if rule.mode == "replace":
                self._wl.set(rule.target_watchlist, symbols)
            elif rule.mode == "union":
                merged = sorted(existing.union(symbols))
                self._wl.set(rule.target_watchlist, merged)
            elif rule.mode == "intersection":
                if not existing:
                    # If nothing existed, treat it as simple set
                    self._wl.set(rule.target_watchlist, symbols)
                else:
                    merged = sorted(existing.intersection(symbols))
                    self._wl.set(rule.target_watchlist, merged)
            else:
                # unknown mode -> treat as replace to be safe
                self._wl.set(rule.target_watchlist, symbols)

    # -----------------------
    # Priority / conflict resolution
    # -----------------------
    def enforce_priority(self, priorities: Sequence[str]) -> None:
        """
        Ensure each symbol appears only in the highest-priority list.

        priorities: ordered list of watchlist names, highest priority first.
        """
        seen = set()
        all_lists: Dict[str, List[str]] = self._wl.all()

        for name in priorities:
            syms = all_lists.get(name, [])
            unique = [s for s in syms if s not in seen]
            self._wl.set(name, unique)
            for s in unique:
                seen.add(s)

        # For any watchlists *not* in priorities, ensure they don't steal symbols
        remaining_names = [n for n in all_lists.keys() if n not in priorities]
        for name in remaining_names:
            syms = self._wl.get(name)
            unique = [s for s in syms if s not in seen]
            self._wl.set(name, unique)
            for s in unique:
                seen.add(s)
