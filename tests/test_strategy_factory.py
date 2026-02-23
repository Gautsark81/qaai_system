# tests/test_strategy_factory.py
from modules.strategy.factory import StrategyFactory, register_strategy
from modules.strategy.examples import MeanReversionStrategy, MomentumStrategy
from modules.strategy.base import Signal
import pytest

def test_factory_registration_and_load():
    # ensure registry contains the example strategies
    reg = StrategyFactory.list_registered()
    assert "MeanReversionStrategy" in reg
    assert "MomentumStrategy" in reg

    # Build strategy via config (registered name)
    cfg = {"type": "MeanReversionStrategy", "strategy_id": "m1", "params": {"window": 5, "z_entry": 0.5, "size": 2}}
    s = StrategyFactory.from_config(cfg)
    assert s.strategy_id == "m1"

    # prepare with a small synthetic history and generate a signal for a price extreme
    history = [{"symbol": "FOO", "price": 100 + i} for i in range(5)]
    s.prepare(history)
    latest = {"symbol": "FOO", "price": 200.0}
    sigs = s.generate_signals(latest)
    assert isinstance(sigs, list)
    assert all(isinstance(x, Signal) for x in sigs)
    assert len(sigs) >= 1

def test_momentum_strategy_signal_direction():
    cfg = {"type": "MomentumStrategy", "strategy_id": "mom1", "params": {"fast": 2, "slow": 3, "size": 1}}
    s = StrategyFactory.from_config(cfg)
    # craft history where fast < slow then new prices push fast > slow
    history = [{"symbol": "BAR", "price": p} for p in [10, 10, 10]]
    s.prepare(history)
    # feed rising prices
    sigs = s.generate_signals({"symbol": "BAR", "price": 11})
    # should produce a BUY (fast > slow)
    assert any(x.side == "BUY" for x in sigs)
