class ColdStartValidator:
    """
    Cold-start safety validator.

    MUST complete successfully before execution starts.
    """

    def __init__(self, reconciler, store):
        self.reconciler = reconciler
        self.store = store

    def validate(self):
        persisted_open_orders = self.store.load_open_orders()
        self.reconciler.reconcile(persisted_open_orders)
