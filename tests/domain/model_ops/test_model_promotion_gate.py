from datetime import datetime
from domain.model_ops.model_promotion_gate import ModelPromotionGate
from domain.model_ops.model_promotion_request import ModelPromotionRequest
from domain.model_ops.model_id import ModelID


def test_promotion_requires_reason():
    req = ModelPromotionRequest(
        model=ModelID("meta", "1.1", "h"),
        requested_by="admin",
        requested_at=datetime.utcnow(),
        reason="",
    )
    assert ModelPromotionGate.allow(req) is False
