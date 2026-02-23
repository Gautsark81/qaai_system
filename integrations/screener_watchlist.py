# qaai_system/integrations/screener_watchlist.py
from __future__ import annotations
from typing import List, Tuple, Any
import logging

log = logging.getLogger(__name__)


def sync_screen_to_watchlist(
    engine: Any,
    watchlist_manager: Any,
    market_df,
    top_k: int = 50,
    score_threshold: float = 0.0,
    explain: bool = False,
) -> List[Tuple[str, float]]:
    """
    Run the screening engine and sync top_k results to the provided watchlist manager.

    Args:
        engine: ScreeningEngineSupercharged-like object with .screen(df, top_k) -> List[(symbol, score)]
        watchlist_manager: object responsible for managing watchlists. Supported APIs:
            - preferred: `update_watchlist(list_of_tuples)` where each tuple is (symbol, score)
            - fallback: `clear()` and `add(symbol, score)` (called repeatedly)
        market_df: full market DataFrame with OHLCV + symbol columns accepted by engine.screen
        top_k: number of top symbols to keep on watchlist
        score_threshold: minimum score to include the symbol (after engine scoring)
        explain: if True, returns full scored list (for debugging). Otherwise returns list pushed.

    Returns:
        list of (symbol, score) that were pushed to watchlist (possibly less than top_k due to threshold).
    """

    # Get screened candidates
    results = engine.screen(
        market_df, top_k=top_k * 3
    )  # get a bit extra to filter by threshold
    # Filter by threshold and take top_k
    filtered = [(s, float(sc)) for s, sc in results if sc >= score_threshold]
    filtered = filtered[:top_k]

    # Attempt preferred API: update_watchlist
    try:
        if hasattr(watchlist_manager, "update_watchlist"):
            log.debug("Using update_watchlist API")
            watchlist_manager.update_watchlist(filtered)
        else:
            # Fallback: clear + add
            log.debug("Using fallback API (clear/add)")
            if hasattr(watchlist_manager, "clear"):
                watchlist_manager.clear()
            for sym, sc in filtered:
                if hasattr(watchlist_manager, "add"):
                    watchlist_manager.add(sym, sc)
                else:
                    # last resort: try setting attribute or raise
                    try:
                        setattr(watchlist_manager, "_last_added", (sym, sc))
                    except Exception:
                        raise RuntimeError(
                            "watchlist_manager does not support update_watchlist or add/clear API"
                        )
    except Exception as e:
        log.exception("Failed to sync screen to watchlist: %s", e)
        raise

    if explain:
        return filtered
    return filtered
