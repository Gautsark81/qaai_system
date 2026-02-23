# tests/test_approved_for_live.py
from qaai_system.execution.order_manager import OrderManager


def test_approved_for_live_defaults_false():
    om = OrderManager(broker=None, config={})
    assert hasattr(om, "approved_for_live")
    assert om.approved_for_live is False


def test_approved_for_live_can_be_enabled_via_config():
    om = OrderManager(broker=None, config={"approved_for_live": True})
    assert om.approved_for_live is True
