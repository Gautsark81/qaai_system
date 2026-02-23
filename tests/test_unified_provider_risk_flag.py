# tests/test_unified_provider_risk_flag.py
from providers.unified_provider import UnifiedProvider
from providers.dhan_provider import DhanProvider
import pytest


class DenyRisk:
    def is_trading_allowed(self, account_equity=None):
        return False


def test_unified_provider_raises_when_raise_on_risk_true():
    dp = DhanProvider(config={"starting_cash": 1000})
    dp.connect()
    up = UnifiedProvider(
        paper_provider=dp,
        live_provider=None,
        default_mode="paper",
        risk_manager=DenyRisk(),
    )
    with pytest.raises(ValueError, match="Trading not allowed"):
        up.submit_order_with_retry(
            {"symbol": "A", "side": "buy", "quantity": 1, "price": 1.0},
            retries=0,
            retry_delay=0,
            raise_on_risk=True,
        )
