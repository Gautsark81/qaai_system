from decimal import Decimal

import pytest

from core.strategy_factory.screening.screening_engine import ScreeningEngine
from core.strategy_factory.screening.regime_overlay import RegimeOverlay
from core.strategy_factory.screening.redundancy_pruner import RedundancyPruner
from core.strategy_factory.screening.ssr_prefilter import SSRPreFilter
from core.strategy_factory.screening.screening_replay_verifier import (
    ScreeningReplayVerifier,
    ScreeningReplayMismatch,
)


def _build_expected_hash():
    engine = ScreeningEngine()
    regime = RegimeOverlay()
    pruner = RedundancyPruner()
    ssr = SSRPreFilter()

    metrics = {
        "A": Decimal("3"),
        "B": Decimal("2"),
        "C": Decimal("1"),
    }

    regime_adj = {
        "A": Decimal("0"),
        "B": Decimal("0"),
        "C": Decimal("0"),
    }

    ssr_map = {
        "A": Decimal("0.9"),
        "B": Decimal("0.6"),
        "C": Decimal("0.1"),
    }

    result = engine.screen(metrics)
    result = regime.apply(result, regime_adj)
    result = pruner.prune(result)
    result = ssr.filter(result, ssr_map, Decimal("0.5"))

    return result.state_hash


def test_screening_replay_success():
    verifier = ScreeningReplayVerifier()

    expected_hash = _build_expected_hash()

    verifier.verify(
        metrics={
            "A": Decimal("3"),
            "B": Decimal("2"),
            "C": Decimal("1"),
        },
        regime_adjustments={
            "A": Decimal("0"),
            "B": Decimal("0"),
            "C": Decimal("0"),
        },
        ssr_map={
            "A": Decimal("0.9"),
            "B": Decimal("0.6"),
            "C": Decimal("0.1"),
        },
        ssr_threshold=Decimal("0.5"),
        expected_hash=expected_hash,
    )


def test_screening_replay_detects_mismatch():
    verifier = ScreeningReplayVerifier()

    with pytest.raises(ScreeningReplayMismatch):
        verifier.verify(
            metrics={
                "A": Decimal("3"),
                "B": Decimal("2"),
            },
            regime_adjustments={
                "A": Decimal("0"),
                "B": Decimal("0"),
            },
            ssr_map={
                "A": Decimal("0.9"),
                "B": Decimal("0.6"),
            },
            ssr_threshold=Decimal("0.5"),
            expected_hash="invalid_hash",
        )