class RouterAdapter:
    """
    Normalizes router.submit signature expected by tests:
        submit(model_id="m1", order={...})
    """

    def __init__(self, router):
        self._router = router

    def submit(self, *, model_id=None, order: dict):
        if not isinstance(order, dict):
            raise ValueError("order must be dict")

        return self._router.submit(order)
