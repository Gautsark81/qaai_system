# tests/test_fill_model_adapter.py
from modules.backtester.fill_model_adapter import FillModelAdapter
from modules.backtester.volumetric_slippage import Order

def test_adapter_falls_back_to_volumetric():
    adapter = FillModelAdapter(ml_infer_fn=None, volumetric_kwargs={"participation_rate":0.1})
    order = Order(order_id="o1", symbol="A", side="BUY", qty=50.0, price=100.0)
    bar = {"close":100.0, "volume":1000}
    filled, price, status = adapter.fill(order, bar, remaining_qty=order.qty)
    # participation_rate 0.1 * 1000 = 100 > 50 so full fill expected
    assert filled == 50.0
    assert status == "filled"

def test_adapter_calls_ml_hook_if_present():
    # make a fake ml hook that always reports a full instant fill at a fixed price
    def fake_ml(order, bar, remaining_qty):
        return {"filled_qty": remaining_qty, "avg_price": 99.5, "status": "filled"}

    adapter = FillModelAdapter(ml_infer_fn=fake_ml)
    order = Order(order_id="o2", symbol="B", side="SELL", qty=20.0, price=100.0)
    bar = {"close":100.0, "volume":100}
    filled, price, status = adapter.fill(order, bar, remaining_qty=order.qty)
    assert filled == 20.0
    assert price == 99.5
    assert status == "filled"
