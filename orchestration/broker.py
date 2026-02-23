class DryRunBroker:
    """
    Broker that records orders but never sends them.
    """

    def __init__(self):
        self.orders = []

    def submit_order(self, order):
        self.orders.append(order)
        return {
            "status": "dropped",
            "reason": "dry_run",
            "order": order,
        }
