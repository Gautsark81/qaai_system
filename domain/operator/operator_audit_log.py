from typing import List
from domain.operator.operator_action import OperatorAction


class OperatorAuditLog:
    """
    Immutable record of operator actions.
    """

    def __init__(self):
        self._log: List[OperatorAction] = []

    def record(self, action: OperatorAction) -> None:
        self._log.append(action)

    def all(self) -> List[OperatorAction]:
        return list(self._log)
