import pytest
from dataclasses import FrozenInstanceError

from core.strategy_factory.health.contracts import StrategyHealthSnapshot


def _make_snapshot() -> StrategyHealthSnapshot:
    return StrategyHealthSnapshot(
        strategy_id="alpha_1",
        total_trades=120,
        win_rate=0.58,
        expectancy=0.32,
        drawdown=0.18,
        volatility=0.21,
        max_consecutive_losses=4,
        ssr=0.74,
        ssr_components={
            "performance": 0.8,
            "risk": 0.7,
            "stability": 0.72,
        },
        warnings=[],
    )


def test_snapshot_is_frozen():
    snap = _make_snapshot()
    with pytest.raises(FrozenInstanceError):
        snap.win_rate = 0.9


def test_ssr_bounds():
    snap = _make_snapshot()
    assert 0.0 <= snap.ssr <= 1.0


def test_ssr_components_are_present():
    snap = _make_snapshot()
    assert isinstance(snap.ssr_components, dict)
    assert len(snap.ssr_components) > 0


def test_warnings_is_list():
    snap = _make_snapshot()
    assert isinstance(snap.warnings, list)


def test_snapshot_is_deterministic():
    s1 = _make_snapshot()
    s2 = _make_snapshot()
    assert s1 == s2


def test_snapshot_fields_are_stable():
    snap = _make_snapshot()
    assert snap.strategy_id == "alpha_1"
    assert snap.total_trades == 120
    assert snap.max_consecutive_losses == 4
