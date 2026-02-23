from datetime import datetime
from domain.model_ops.model_promotion_request import ModelPromotionRequest
from domain.model_ops.model_id import ModelID


def test_promotion_request_fields():
    r = ModelPromotionRequest(
        model=ModelID("meta", "1.1", "h"),
        requested_by="admin",
        requested_at=datetime.utcnow(),
        reason="Better calibration",
    )
    assert r.requested_by == "admin"
