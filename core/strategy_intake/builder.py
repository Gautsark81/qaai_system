from typing import Iterable, Dict, Any, Optional, List
from datetime import datetime, timezone

from core.strategy_intake.models import (
    SignalCandidate,
    StrategyIntakeBatch,
)
from core.strategy_intake.gates import (
    gate_min_confidence,
    gate_max_symbols,
)
from core.watchlist.models import WatchlistEntry


class StrategyIntakeBuilder:
    """
    Converts Watchlist → Strategy Intake Batch
    """

    def __init__(
        self,
        min_confidence: float = 0.0,
        max_symbols: Optional[int] = None,
    ):
        self.min_confidence = float(min_confidence)
        self.max_symbols = max_symbols

    def build(
        self,
        watchlist: Iterable[WatchlistEntry],
        features: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> StrategyIntakeBatch:

        features = features or {}

        candidates: List[SignalCandidate] = []

        for w in watchlist:
            candidates.append(
                SignalCandidate(
                    symbol=w.symbol,
                    rank=w.rank,
                    confidence=w.confidence,
                    source=w.source,
                    features=features.get(w.symbol, {}),
                    reasons=list(w.reasons),
                )
            )

        # --- Gates ---
        candidates = gate_min_confidence(
            candidates,
            self.min_confidence,
        )

        if self.max_symbols is not None:
            candidates = gate_max_symbols(
                candidates,
                self.max_symbols,
            )

        return StrategyIntakeBatch(
            generated_at=datetime.now(timezone.utc),
            candidates=candidates,
            constraints={
                "min_confidence": self.min_confidence,
                "max_symbols": self.max_symbols,
                "input_count": len(list(watchlist)),
                "final_count": len(candidates),
            },
        )
