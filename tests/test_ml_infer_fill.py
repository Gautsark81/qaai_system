# tests/test_ml_infer_fill.py
import pytest
from modules.backtester.fill_model_adapter import FillModelAdapter
from modules.backtester.volumetric_slippage import Order
import importlib
import ml.infer_fill as infer_mod

def test_default_infer_fill_returns_expected_keys():
    order = Order(order_id="m1", symbol="S", side="BUY", qty=100.0, price=50.0)
    bar = {"close": 50.0, "volume": 1000.0}
    res = infer_mod.infer_fill(order, bar, remaining_qty=order.qty)
    assert isinstance(res, dict)
    assert set(res.keys()) >= {"filled_qty", "avg_price", "status"}

def test_adapter_uses_default_ml_hook(monkeypatch):
    # Ensure adapter picks up ml.infer_fill.infer_fill automatically
    order = Order(order_id="m2", symbol="S", side="BUY", qty=10.0, price=10.0)
    bar = {"close": 10.0, "volume": 1000.0}
    adapter = FillModelAdapter(ml_infer_fn=None, volumetric_kwargs={"participation_rate": 0.01})
    filled, price, status = adapter.fill(order, bar, remaining_qty=order.qty)
    # default infer_fill uses default_participation=0.1 => capacity 100 -> target min(10,100)=10 => filled
    assert filled == pytest.approx(10.0)
    assert status == "filled"
