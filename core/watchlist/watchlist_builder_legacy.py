"""
LEGACY WATCHLIST BUILDER (FROZEN)

⚠️ Pre O-1.1 architecture
⚠️ Uses deprecated screening contracts
⚠️ Retained ONLY for historical replay / audit

DO NOT USE FOR NEW PIPELINES
"""

# Original content preserved intentionally
from core.contracts.screening import ScreeningResult
from core.contracts.watchlist import WatchlistManifest


class LegacyWatchlistBuilder:
    def build(self, screening_results: list[ScreeningResult]) -> WatchlistManifest:
        return WatchlistManifest.from_screening(screening_results)
