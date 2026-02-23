# tests/test_risk_enforced_at_provider_and_unified.py
import pytest
from providers.unified_provider import UnifiedProvider
from providers.dhan_provider import DhanProvider
from providers.dhan_http import DhanHTTPProvider


class DenyRisk:
    def is_trading_allowed(self, account_equity=None):
        return False


def test_unified_provider_blocks_when_raise_on_risk_true():
    base = DhanProvider(config={"starting_cash": 1000})
    base.connect()
    up = UnifiedProvider(
        paper_provider=base, live_provider=None, default_mode="paper", risk_manager=None
    )
    with pytest.raises(ValueError, match="Trading not allowed"):
        up.submit_order_with_retry(
            {"symbol": "A", "side": "buy", "quantity": 1, "price": 1.0},
            retries=0,
            retry_delay=0,
            raise_on_risk=True,
        )

    # attach deny risk to wrapper should raise immediately
    up.set_risk_manager(DenyRisk())
    with pytest.raises(ValueError, match="Trading not allowed"):
        up.submit_order_with_retry(
            {"symbol": "A", "side": "buy", "quantity": 1, "price": 1.0},
            retries=0,
            retry_delay=0,
            raise_on_risk=True,
        )


def test_provider_blocks_when_risk_attached():
    base = DhanProvider(config={"starting_cash": 1000})
    base.connect()
    base.set_risk_manager(DenyRisk())
    # direct provider call should raise
    with pytest.raises(ValueError, match="Trading not allowed"):
        base.submit_order({"symbol": "A", "side": "buy", "quantity": 1, "price": 1.0})


def test_dhan_http_provider_blocks_when_risk_attached():
    dp = DhanHTTPProvider(config={"starting_cash": 1000, "enable_http": False})
    dp.connect()
    dp.set_risk_manager(DenyRisk())
    with pytest.raises(ValueError, match="Trading not allowed"):
        dp.submit_order({"symbol": "A", "side": "buy", "quantity": 1, "price": 1.0})
