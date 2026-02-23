from domain.model_ops.active_model_pointer import ActiveModelPointer
from domain.model_ops.model_id import ModelID


def test_active_model_set_and_get():
    p = ActiveModelPointer()
    m = ModelID("meta", "1.0", "h")
    p.set(m)
    assert p.get() == m
