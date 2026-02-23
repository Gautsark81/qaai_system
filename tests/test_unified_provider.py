# tests/test_unified_provider.py
from providers.unified_provider import UnifiedProvider
from providers.dhan_provider import DhanProvider
from data.ingestion.paper_provider import PaperProvider


def test_unified_switch_modes(tmp_path):
    pp = PaperProvider(config={"starting_cash": 1000})
    dp = DhanProvider(config={"starting_cash": 1000})
    up = UnifiedProvider(paper_provider=pp, live_provider=dp, default_mode="paper")
    # paper submit
    r1 = up.submit_order({"symbol": "A", "side": "buy", "quantity": 1, "price": 1.0})
    assert isinstance(r1, dict)
    # switch to live
    up.set_mode("live")
    r2 = up.submit_order({"symbol": "A", "side": "buy", "quantity": 1, "price": 1.0})
    assert isinstance(r2, dict)
    assert up.get_account_nav() is not None
    assert isinstance(up.get_positions(), dict)
