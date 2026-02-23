from domain.model_ops.model_promotion_request import ModelPromotionRequest


class ModelPromotionGate:
    """
    Governs whether a model may be promoted.
    """

    @staticmethod
    def allow(req: ModelPromotionRequest) -> bool:
        if not req.reason:
            return False
        if not req.requested_by:
            return False
        return True
