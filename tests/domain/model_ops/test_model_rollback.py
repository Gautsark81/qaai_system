from domain.model_ops.model_rollback import ModelRollback
from domain.model_ops.active_model_pointer import ActiveModelPointer
from domain.model_ops.model_id import ModelID


def test_model_rollback_sets_previous():
    ptr = ActiveModelPointer()
    old = ModelID("meta", "1.0", "h1")
    ModelRollback.rollback(ptr, old)
    assert ptr.get() == old
