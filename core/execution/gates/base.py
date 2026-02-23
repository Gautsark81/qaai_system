from abc import ABC, abstractmethod


class ExecutionGate(ABC):
    """
    Stateless execution gate contract.
    """

    @abstractmethod
    def evaluate(self, context):
        raise NotImplementedError
