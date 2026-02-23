from domain.model_ops.active_model_pointer import ActiveModelPointer
from domain.model_ops.model_id import ModelID


class ModelRollback:
    """
    Allows safe rollback to a previous model.
    """

    @staticmethod
    def rollback(
        pointer: ActiveModelPointer,
        previous: ModelID,
    ) -> None:
        pointer.set(previous)
