class FakeBroker:
    def __init__(self):
        self._open_orders = []
        self.cancelled = []

    def fetch_open_orders(self):
        return list(self._open_orders)

    def cancel(self, order_id):
        self.cancelled.append(order_id)


class BrokerFactory:
    @staticmethod
    def create(config):
        return FakeBroker()
