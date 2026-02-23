from modules.live_control.failover_router import FailoverRouter

class FailingBroker:
    def place_order(self, _):
        raise RuntimeError("down")

class BackupBroker:
    def __init__(self):
        self.orders = []
    def place_order(self, order):
        self.orders.append(order)
        return "OK"

def test_failover_under_broker_failure():
    router = FailoverRouter(FailingBroker(), BackupBroker())
    assert router.place_order({"id": 1}) == "OK"
