from qaai_system.execution.order_router import OrderRouter


class DummyProvider:
    def submit_order(self, order):
        return "child1"

    def fetch_fills_for_order_ids(self, ids):
        return []


def test_kill_switch_blocks(tmp_path):
    kill_file = tmp_path / "kill.switch"
    cfg = {
        "risk": {"kill_switch_file": str(kill_file)},
        "starting_cash": 1_000_000,
    }
    router = OrderRouter(DummyProvider(), config=cfg)

    plan = {"symbol": "AAPL", "side": "buy", "qty": 10, "price": 100}

    # Initially allowed
    resp1 = router.submit(plan)
    assert resp1["status"] == "submitted"

    # Activate kill switch
    kill_file.write_text("1")
    resp2 = router.submit(plan)
    assert resp2["status"] == "blocked"
    assert "kill" in resp2["reason"].lower()
