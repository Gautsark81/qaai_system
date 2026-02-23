from domain.model_ops.model_registry import ModelRegistry
from domain.model_ops.active_model_pointer import ActiveModelPointer
from domain.model_ops.model_promotion_gate import ModelPromotionGate
from domain.model_ops.model_promotion_request import ModelPromotionRequest


class ModelPromotionService:
    """
    Wires registry, gate, and active pointer.
    """

    def __init__(
        self,
        registry: ModelRegistry,
        pointer: ActiveModelPointer,
    ):
        self.registry = registry
        self.pointer = pointer

    def promote(self, req: ModelPromotionRequest) -> bool:
        if not ModelPromotionGate.allow(req):
            return False

        model = self.registry.get(req.model.name, req.model.version)
        if not model:
            return False

        self.pointer.set(model)
        return True
