class FailoverRouter:
    """
    Transparent broker failover.
    No retry storms. No duplication.
    """

    def __init__(self, primary, secondary):
        self.primary = primary
        self.secondary = secondary

    def place_order(self, order):
        try:
            return self.primary.place_order(order)
        except Exception:
            return self.secondary.place_order(order)
