from qaai_system.execution.order_router import OrderRouter


class DummyProvider:
    def submit_order(self, order):
        return "child1"

    def fetch_fills_for_order_ids(self, ids):
        return []


def test_daily_loss_limit_blocks():
    cfg = {
        "risk": {"daily_loss_limit": 0.02},
        "starting_cash": 1_000_000,
    }
    router = OrderRouter(DummyProvider(), config=cfg)

    plan = {"symbol": "AAPL", "side": "buy", "qty": 10, "price": 100}

    # Inject a big loss into trade history
    router.risk.update_trade_log({"symbol": "AAPL", "pnl": -25_000, "status": "closed"})

    resp = router.submit(plan)
    assert resp["status"] == "blocked"
    assert "daily loss" in (resp.get("reason") or "").lower()
