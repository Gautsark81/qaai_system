from qaai_system.execution.order_router import OrderRouter

class DummyProvider:
    def submit_order(self, order):
        return "child1"

    def fetch_fills_for_order_ids(self, ids):
        return []


def test_circuit_breaker_blocks(tmp_path):
    cfg = {
        "risk": {
            "kill_switch_file": str(tmp_path / "kill.switch"),
            "max_drawdown_pct": 5.0,
        },
        "starting_cash": 1_000_000,
    }
    router = OrderRouter(DummyProvider(), config=cfg)

    plan = {"symbol": "AAPL", "side": "buy", "qty": 10, "price": 100}

    # Equity still healthy (2% DD < 5%)
    router.account_equity = 980_000
    resp1 = router.submit(plan)
    assert resp1["status"] == "submitted"

    # Breach drawdown (6% DD > 5%)
    router.account_equity = 940_000
    resp2 = router.submit(plan)
    assert resp2["status"] == "blocked"
    assert "drawdown" in (resp2.get("reason") or "").lower()
