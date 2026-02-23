from data.execution import ExecutionIntent, IntentStore, ExecutionState


class IdempotentOrderExecutor:
    """
    Exactly-once execution wrapper around OrderManager.
    """

    def __init__(self, *, order_manager, intent_store: IntentStore):
        self._om = order_manager
        self._store = intent_store

    def execute(self, intent: ExecutionIntent) -> ExecutionState:
        state = self._store.put(intent)

        if state != ExecutionState.NEW:
            # Already submitted or completed
            return state

        # Use deterministic intent_id as internal order_id
        order_id = self._om.create_order(
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            price=intent.price,
            meta={
                "execution_intent_id": intent.intent_id,
                "strategy_id": intent.strategy_id,
                "feature_manifest_id": intent.feature_manifest_id,
                "model_id": intent.model_id,
            },
            _internal_id=intent.intent_id,  # 🔒 critical
        )

        if order_id:
            self._store.transition(intent.intent_id, ExecutionState.SENT)
            return ExecutionState.SENT

        self._store.transition(intent.intent_id, ExecutionState.FAILED)
        return ExecutionState.FAILED
