class DummyBroker:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.orders = []

    def place_order(self, order):
        if self.should_fail:
            raise RuntimeError("Broker down")
        self.orders.append(order)
        return "OK"


from modules.live_control.failover_router import FailoverRouter


def test_failover_to_secondary():
    primary = DummyBroker(should_fail=True)
    secondary = DummyBroker()

    router = FailoverRouter(primary, secondary)

    result = router.place_order({"id": 1})

    assert result == "OK"
    assert len(secondary.orders) == 1
