import pytest
from core.strategy_factory.ensemble import EnsembleSnapshot, EnsembleStrategy


def test_snapshot_is_immutable():
    strategies = [EnsembleStrategy("S1", 90)]
    snap = EnsembleSnapshot(strategies, 1000, 1000, 1000, 1000)

    with pytest.raises(Exception):
        snap.available_capital = 2000