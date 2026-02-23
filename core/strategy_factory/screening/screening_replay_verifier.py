# core/strategy_factory/screening/screening_replay_verifier.py

from __future__ import annotations

from decimal import Decimal
from typing import Dict

from .screening_engine import ScreeningEngine
from .regime_overlay import RegimeOverlay
from .redundancy_pruner import RedundancyPruner
from .ssr_prefilter import SSRPreFilter


class ScreeningReplayMismatch(Exception):
    pass


class ScreeningReplayVerifier:
    """
    C5.5 — Deterministic Replay Verifier for Screening Pipeline

    HARD RULES:
    - No mutation
    - No authority
    - No registry access
    - Pure verification
    """

    def __init__(self):
        self.engine = ScreeningEngine()
        self.regime = RegimeOverlay()
        self.pruner = RedundancyPruner()
        self.ssr = SSRPreFilter()

    def verify(
        self,
        *,
        metrics: Dict[str, Decimal],
        regime_adjustments: Dict[str, Decimal],
        ssr_map: Dict[str, Decimal],
        ssr_threshold: Decimal,
        expected_hash: str,
    ) -> None:

        # Step 1 — Raw screening
        result = self.engine.screen(metrics)

        # Step 2 — Regime overlay
        result = self.regime.apply(result, regime_adjustments)

        # Step 3 — Redundancy prune
        result = self.pruner.prune(result)

        # Step 4 — SSR prefilter
        result = self.ssr.filter(result, ssr_map, ssr_threshold)

        if result.state_hash != expected_hash:
            raise ScreeningReplayMismatch(
                f"Replay mismatch: expected {expected_hash}, got {result.state_hash}"
            )