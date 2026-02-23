# core/runtime/runtime_contract.py
class RuntimeContractViolation(RuntimeError):
    pass


class RuntimeContract:
    """
    Enforces immutability of runtime-critical state.
    """

    IMMUTABLE_KEYS = {
        "capital_limits",
        "risk_limits",
        "strategy_definitions",
    }

    def __init__(self, state: dict):
        self._initial = dict(state)

    def validate(self, new_state: dict):
        for k in self.IMMUTABLE_KEYS:
            if self._initial.get(k) != new_state.get(k):
                raise RuntimeContractViolation(
                    f"Immutable runtime field modified: {k}"
                )
