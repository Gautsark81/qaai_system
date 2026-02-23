class PaperLedger:
    """
    Idempotency + persistence layer.
    """

    def __init__(self):
        self._orders = {}  # order_id -> result

    def has(self, order_id: str) -> bool:
        return order_id in self._orders

    def record(self, order_id: str, result: dict):
        self._orders[order_id] = result

    def get(self, order_id: str):
        return self._orders[order_id]
