from datetime import datetime
from domain.model_ops.model_registry import ModelRegistry
from domain.model_ops.active_model_pointer import ActiveModelPointer
from domain.model_ops.model_promotion_service import ModelPromotionService
from domain.model_ops.model_promotion_request import ModelPromotionRequest
from domain.model_ops.model_id import ModelID


def test_model_promotion_flow():
    reg = ModelRegistry()
    ptr = ActiveModelPointer()
    svc = ModelPromotionService(reg, ptr)

    m = ModelID("meta", "2.0", "h2")
    reg.register(m)

    req = ModelPromotionRequest(
        model=m,
        requested_by="admin",
        requested_at=datetime.utcnow(),
        reason="Improved stability",
    )

    assert svc.promote(req) is True
    assert ptr.get() == m
