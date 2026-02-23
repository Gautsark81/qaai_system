from dataclasses import dataclass
from datetime import datetime
from domain.model_ops.model_id import ModelID


@dataclass(frozen=True)
class ModelPromotionRequest:
    model: ModelID
    requested_by: str
    requested_at: datetime
    reason: str
