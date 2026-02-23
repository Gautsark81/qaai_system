from execution.shadow.shadow_router import ShadowRouter


def test_shadow_router_no_real_execution():
    router = ShadowRouter()
    res = router.submit({"symbol": "TST", "price": 100, "qty": 1})
    assert res["status"] == "FILLED"
