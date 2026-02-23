class DummyRouter:
    """
    Test stub router.
    Always fills immediately.
    """

    def submit(self, plan):
        return {"status": "filled"}

    def cancel(self, order_id: str):
        return {"order_id": order_id, "status": "CANCELLED"}
