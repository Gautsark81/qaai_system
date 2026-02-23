from abc import ABC, abstractmethod
from typing import Any

from core.execution.broker_response.models import BrokerResponse


class BrokerAdapter(ABC):

    @abstractmethod
    def normalize(self, raw: Any) -> BrokerResponse:
        """
        Convert raw broker response into canonical BrokerResponse.
        Must be deterministic and side-effect free.
        """
        raise NotImplementedError
