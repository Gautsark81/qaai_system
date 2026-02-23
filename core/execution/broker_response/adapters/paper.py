from datetime import datetime

from core.execution.broker_response.adapters.base import BrokerAdapter
from core.execution.broker_response.models import BrokerResponse


class PaperBrokerAdapter(BrokerAdapter):
    """
    Deterministic adapter for PAPER broker responses.

    Guarantees:
    - Raw payload is NOT retained
    - Same raw input → identical BrokerResponse
    - Canonical field mapping only
    """

    def normalize(self, raw: dict) -> BrokerResponse:
        return BrokerResponse(
            broker="PAPER",
            order_id=str(raw.get("order_id", "PAPER-UNKNOWN")),
            status="FILLED",
            filled_quantity=int(raw.get("quantity", 0)),
            avg_price=float(raw.get("price", 0.0)),
            timestamp=datetime.utcfromtimestamp(0),  # 🔒 deterministic
            rejection_reason=None,
        )
