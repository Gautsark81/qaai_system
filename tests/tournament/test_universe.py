import pytest
from modules.tournament.universe import TradingUniverse


def test_universe_valid():
    u = TradingUniverse(["A"] * 50)
    assert len(u.symbols) == 50


def test_universe_too_small():
    with pytest.raises(ValueError):
        TradingUniverse(["A"] * 10)
