from domain.model_ops.model_registry import ModelRegistry
from domain.model_ops.model_id import ModelID


def test_domain_model_registry_register_and_get():
    r = ModelRegistry()
    m = ModelID("meta", "1.0", "h1")
    r.register(m)
    assert r.get("meta", "1.0") == m
