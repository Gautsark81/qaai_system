from data.execution import IntentStore, ExecutionState
from data.execution.errors import ExecutionError


class ExecutionReconciler:
    """
    Idempotent reconciliation of broker events.

    Safe to call multiple times.
    Safe across restarts.
    """

    def __init__(self, *, intent_store: IntentStore):
        self._store = intent_store

    # ----------------------------
    # Broker ACK
    # ----------------------------

    def on_ack(self, intent_id: str) -> ExecutionState:
        """
        Broker acknowledged order acceptance.
        """
        current = self._store.state(intent_id)

        if current is None:
            raise ExecutionError("unknown intent")

        if current == ExecutionState.SENT:
            return self._store.transition(intent_id, ExecutionState.ACKED)

        # Duplicate / out-of-order ACK → ignore safely
        return current

    # ----------------------------
    # Broker FILL
    # ----------------------------

    def on_fill(self, intent_id: str) -> ExecutionState:
        """
        Broker reported full fill.

        Fill is terminal and may arrive without ACK.
        """
        current = self._store.state(intent_id)

        if current is None:
            raise ExecutionError("unknown intent")

        if current == ExecutionState.SENT:
            # Implicit ACK before FILL (broker skipped ACK)
            self._store.transition(intent_id, ExecutionState.ACKED)
            return self._store.transition(intent_id, ExecutionState.FILLED)

        if current == ExecutionState.ACKED:
            return self._store.transition(intent_id, ExecutionState.FILLED)

        # Duplicate / out-of-order fill → ignore safely
        return current

    # ----------------------------
    # Broker FAILURE
    # ----------------------------

    def on_failure(self, intent_id: str) -> ExecutionState:
        current = self._store.state(intent_id)

        if current is None:
            raise ExecutionError("unknown intent")

        if current == ExecutionState.SENT:
            return self._store.transition(intent_id, ExecutionState.FAILED)

        return current
